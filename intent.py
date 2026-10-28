"""
Intent Routing and Skill Dispatch Engine for Mini-Alexa.

Features:
- RapidFuzz similarity matching for resilient keyword tolerance.
- Multi-skill dispatching with argument inspection.
- Sliding-window conversation memory maintaining the last 5 turns.
- LLM API fallback (Gemini or OpenAI) with conversation context.
- Centralized event logging to `logs/assistant.log`.
- Crash-proof top-level exception handling.
"""

import inspect
import logging
import os
import re
from typing import Callable, Dict, List, Tuple
from rapidfuzz import fuzz
import requests
import config

# Skill module handlers
from skills.time_date import get_time, get_date
from skills.weather import get_weather
from skills.wikipedia_search import search_wikipedia
from skills.jokes import tell_joke
from skills.music import play_music
from skills.system_apps import open_app
from skills.screenshot import take_screenshot
from skills.volume import control_volume
from skills.reminders import set_reminder
from skills.todo import manage_todo
from skills.notes import take_note

# ==============================================================================
# 1. Logging Setup (logs/ Folder)
# ==============================================================================
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "assistant.log")

logger = logging.getLogger("mini_alexa")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# ==============================================================================
# 2. Conversation Memory (Last 5 Exchanges)
# ==============================================================================
CONVERSATION_HISTORY: List[Dict[str, str]] = []

def get_conversation_history() -> List[Dict[str, str]]:
    """Return a copy of recent conversational exchanges."""
    return list(CONVERSATION_HISTORY)

def clear_conversation_history():
    """Reset the stored conversation exchanges."""
    global CONVERSATION_HISTORY
    CONVERSATION_HISTORY = []

def _record_exchange(command: str, response: str):
    """
    Append user command and assistant response to conversation memory,
    strictly maintaining the most recent 5 turns.
    """
    global CONVERSATION_HISTORY
    CONVERSATION_HISTORY.append({"user": command, "assistant": response})
    if len(CONVERSATION_HISTORY) > 5:
        CONVERSATION_HISTORY = CONVERSATION_HISTORY[-5:]

# ==============================================================================
# 3. Skill Registry & Dynamic Registration
# ==============================================================================
SKILL_REGISTRY: Dict[Tuple[str, ...], Callable] = {}

def register_skill(keywords: List[str] | Tuple[str, ...] | str, handler: Callable):
    """
    Register a skill handler for one or more trigger keywords.

    Parameters:
        keywords (list | tuple | str): Keywords or phrases triggering this skill.
        handler (Callable): Target function executing the skill.
    """
    if isinstance(keywords, str):
        keywords = (keywords,)
    key_tuple = tuple(k.strip().lower() for k in keywords)
    SKILL_REGISTRY[key_tuple] = handler

# Register built-in skills in order of keyword specificity
register_skill(["time", "clock"], get_time)
register_skill(["date", "day", "today"], get_date)
register_skill(
    ["volume up", "volume down", "increase volume", "decrease volume", "lower volume", "raise volume", "mute", "unmute", "louder", "quieter", "volume"],
    control_volume,
)
register_skill(["screenshot", "capture screen", "snapshot"], take_screenshot)
register_skill(["remind me", "reminder", "set a reminder", "set reminder"], set_reminder)
register_skill(["to-do", "todo", "task", "tasks"], manage_todo)
register_skill(["take a note", "write a note", "make a note", "create a note", "note down", "notes", "note that", "note"], take_note)
register_skill(["play song", "play music", "play on youtube", "play"], play_music)
register_skill(["open", "launch", "start"], open_app)
register_skill(["weather", "temperature", "forecast", "climate"], get_weather)
register_skill(["joke", "jokes", "funny", "make me laugh"], tell_joke)
register_skill(["who is", "what is", "tell me about", "wikipedia", "search"], search_wikipedia)

# ==============================================================================
# 4. Fuzzy Keyword Matching
# ==============================================================================
# Keywords matched strictly via exact substring to avoid false positives with question words
EXACT_ONLY_KEYWORDS = {"who is", "what is", "where is", "open", "play"}

def _matches_keywords(cmd_clean: str, keywords: Tuple[str, ...]) -> bool:
    """
    Determine if the command matches any keyword via exact or fuzzy string comparison.

    Parameters:
        cmd_clean (str): Normalized lowercase user command.
        keywords (tuple): Set of trigger phrases for a skill.

    Returns:
        bool: True if a matching trigger keyword is identified.
    """
    # 1. Exact substring match
    if any(kw in cmd_clean for kw in keywords):
        return True

    # 2. Fuzzy match via rapidfuzz
    cmd_words = cmd_clean.split()
    for kw in keywords:
        if kw in EXACT_ONLY_KEYWORDS:
            continue

        if " " in kw:
            # Multi-word phrase fuzzy comparison
            if fuzz.partial_ratio(kw, cmd_clean) >= 85:
                return True
        else:
            # Single-word keyword comparison against individual command words
            for word in cmd_words:
                if fuzz.ratio(kw, word) >= 85:
                    return True

    return False

# ==============================================================================
# 5. LLM API Fallback
# ==============================================================================
def ask_llm(question: str) -> str:
    """
    Submit an unhandled question to an external LLM API (NVIDIA NIM, Gemini, or OpenAI).

    Parameters:
        question (str): The user query.

    Returns:
        str: Concise answer suitable for voice synthesis.
    """
    api_key = getattr(config, "LLM_API_KEY", "")
    provider = getattr(config, "LLM_PROVIDER", "nvidia").lower()
    model = getattr(config, "LLM_MODEL", "nvidia/nemotron-3.5-bolt-e4b")
    base_url = getattr(config, "LLM_BASE_URL", "https://integrate.api.nvidia.com/v1/chat/completions")

    if not api_key or api_key == "YOUR_LLM_API_KEY_HERE":
        logger.warning("LLM API key is not configured in .env")
        return "I don't have an answer for that, and no LLM API key is configured in the .env file."

    system_instruction = (
        "You are Mini-Alexa, a concise and friendly voice assistant. "
        "Answer the question directly in 1 to 2 short sentences suitable for text-to-speech. "
        "Do not include internal reasoning, thinking tags, or markdown headers."
    )

    try:
        # --- Gemini REST API ---
        if provider == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

            contents = []
            for exchange in CONVERSATION_HISTORY:
                contents.append({"role": "user", "parts": [{"text": exchange["user"]}]})
                contents.append({"role": "model", "parts": [{"text": exchange["assistant"]}]})
            contents.append({"role": "user", "parts": [{"text": question}]})

            payload = {
                "contents": contents,
                "systemInstruction": {"parts": [{"text": system_instruction}]},
                "generationConfig": {
                    "maxOutputTokens": 120,
                    "temperature": 0.7,
                },
            }

            response = requests.post(url, json=payload, timeout=12)
            if response.status_code == 200:
                data = response.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return re.sub(r"<(thought|think)>.*?</\1>", "", reply, flags=re.DOTALL).strip()
            else:
                logger.error(f"Gemini API returned status {response.status_code}: {response.text}")
                return "Sorry, I had trouble getting an answer from the AI service."

        # --- NVIDIA NIM & OpenAI-compatible REST API ---
        else:
            url = base_url if base_url else (
                "https://integrate.api.nvidia.com/v1/chat/completions"
                if provider == "nvidia"
                else "https://api.openai.com/v1/chat/completions"
            )
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            messages = [{"role": "system", "content": system_instruction}]
            for exchange in CONVERSATION_HISTORY:
                messages.append({"role": "user", "content": exchange["user"]})
                messages.append({"role": "assistant", "content": exchange["assistant"]})
            messages.append({"role": "user", "content": question})

            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7,
            }

            response = requests.post(url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                choice = data["choices"][0]["message"]
                reply = choice.get("content") or choice.get("reasoning_content") or ""
                clean_reply = re.sub(r"<(thought|think)>.*?</\1>", "", reply, flags=re.DOTALL).strip()
                return clean_reply if clean_reply else reply.strip()
            else:
                logger.error(f"{provider.upper()} API returned status {response.status_code}: {response.text}")
                return "Sorry, I had trouble getting an answer from the AI service."

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        logger.error("LLM API request connection error or timeout.")
        return "I could not connect to the AI service. Please check your internet connection."
    except Exception as err:
        logger.error(f"Unexpected error querying LLM: {err}")
        return "Sorry, an unexpected error occurred while consulting the AI service."

# ==============================================================================
# 6. Primary Intent Dispatcher
# ==============================================================================
def handle(command: str) -> str:
    """
    Main dispatch function:
    1. Logs incoming voice command.
    2. Searches registry for matching skills (using exact and fuzzy matching).
    3. Falls back to conversational LLM API if no local skill matches.
    4. Logs response and updates conversation memory.
    5. Wraps all logic in error handling to ensure continuous assistant uptime.

    Parameters:
        command (str): The voice transcription string.

    Returns:
        str: The verbal response message.
    """
    if not command:
        return "Sorry, I didn't get that."

    cmd_clean = command.strip().lower()
    logger.info(f"Incoming Command: '{cmd_clean}'")

    response_text = ""
    try:
        # Step 1: Match against registered skill triggers
        matched_handler = None
        for keywords, handler in SKILL_REGISTRY.items():
            if _matches_keywords(cmd_clean, keywords):
                matched_handler = handler
                logger.info(f"Matched Skill: {handler.__name__} (keywords: {keywords})")
                break

        if matched_handler:
            try:
                sig = inspect.signature(matched_handler)
                if len(sig.parameters) > 0:
                    response_text = matched_handler(cmd_clean)
                else:
                    response_text = matched_handler()
            except Exception as skill_err:
                logger.error(f"Error in skill '{matched_handler.__name__}': {skill_err}", exc_info=True)
                response_text = "Sorry, I encountered an error executing that skill."
        else:
            # Step 2: Route to LLM conversational fallback
            logger.info("No skill matched. Routing to LLM API fallback...")
            response_text = ask_llm(cmd_clean)

    except Exception as top_err:
        logger.critical(f"Critical error in intent dispatch: {top_err}", exc_info=True)
        response_text = "I encountered an error while processing that, but I am still online."

    if not response_text:
        response_text = "Sorry, I didn't get that."

    # Update conversation history and write response to log
    _record_exchange(cmd_clean, response_text)
    logger.info(f"Response: '{response_text}'")

    return response_text
