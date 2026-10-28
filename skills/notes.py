"""Notes skill for Mini-Alexa to dictate notes and append them with timestamps to notes.txt."""

import datetime
import os
import re
from listener import listen
from speaker import speak

NOTES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "notes.txt")

def take_note(command: str = "") -> str:
    """
    Take a dictated voice note and append it with a timestamp to notes.txt.
    Prompts the user for note content if not provided in the command.
    """
    note_text = ""

    if command:
        # Strip trigger phrases from command
        cleaned = re.sub(
            r"^(take\s+a\s+note\s+that|take\s+a\s+note|write\s+a\s+note|make\s+a\s+note|create\s+a\s+note|note\s+down|note\s+that|note)\s*",
            "",
            command.strip(),
            flags=re.IGNORECASE,
        ).strip()
        if cleaned:
            note_text = cleaned

    # If no note text in command, prompt the user and listen for dictation
    if not note_text:
        speak("What would you like me to note down?")
        note_text = listen()

    if not note_text:
        return "I didn't catch that, so no note was saved."

    # Format timestamp and append to notes.txt
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    note_entry = f"[{timestamp}] {note_text}\n"

    try:
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(note_entry)
        return f"Note recorded and saved: '{note_text}'."
    except Exception as e:
        return f"Failed to save note: {e}"
