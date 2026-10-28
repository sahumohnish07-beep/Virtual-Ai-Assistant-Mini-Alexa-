"""
Configuration Module for Mini-Alexa.

Loads runtime environment variables from a `.env` file using `python-dotenv`
and provides centralized access to application-wide settings such as API keys,
wake word triggers, and speech synthesis parameters.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file located in the project root
load_dotenv()

# ==============================================================================
# Wake Word Settings
# ==============================================================================
# The keyword used to activate Mini-Alexa from passive listening mode
WAKE_WORD: str = os.getenv("WAKE_WORD", "jarvis").strip().lower()

# ==============================================================================
# Weather API Settings
# ==============================================================================
# OpenWeatherMap API Key for live weather reporting
WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "YOUR_WEATHER_API_KEY_HERE").strip()

# Default city used when the user asks for weather without specifying a location
DEFAULT_CITY: str = os.getenv("DEFAULT_CITY", "Pune").strip()

# ==============================================================================
# LLM Fallback Settings
# ==============================================================================
# API key for the conversational AI fallback service (NVIDIA, Gemini, or OpenAI)
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "YOUR_LLM_API_KEY_HERE").strip()

# Provider type: 'nvidia' (default), 'gemini', or 'openai'
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "nvidia").strip().lower()

# Target model identifier (e.g. 'nvidia/nemotron-3.5-bolt-e4b', 'gemini-1.5-flash', 'gpt-4o-mini')
default_model = "nvidia/nemotron-3.5-bolt-e4b" if LLM_PROVIDER == "nvidia" else "gemini-1.5-flash"
LLM_MODEL: str = os.getenv("LLM_MODEL", default_model).strip()

# Endpoint URL for OpenAI-compatible or NVIDIA APIs
default_base_url = (
    "https://integrate.api.nvidia.com/v1/chat/completions"
    if LLM_PROVIDER == "nvidia"
    else "https://api.openai.com/v1/chat/completions"
)
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", default_base_url).strip()

# ==============================================================================
# Speech Synthesis (TTS) Settings
# ==============================================================================
# Voice speech rate in words per minute (typical default: ~175-200)
try:
    VOICE_RATE: int = int(os.getenv("VOICE_RATE", "175"))
except ValueError:
    VOICE_RATE: int = 175

# Volume level on a scale from 0.0 (silent) to 1.0 (full volume)
try:
    VOICE_VOLUME: float = float(os.getenv("VOICE_VOLUME", "1.0"))
except ValueError:
    VOICE_VOLUME: float = 1.0

# Aliases for backwards compatibility with earlier modules
SPEECH_RATE: int = VOICE_RATE
VOLUME_LEVEL: float = VOICE_VOLUME
