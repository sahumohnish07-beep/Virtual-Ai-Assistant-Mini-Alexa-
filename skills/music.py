"""Music skill for Mini-Alexa to play songs on YouTube using pywhatkit."""

import re
import pywhatkit

def play_music(command: str) -> str:
    """
    Extract song title from command and play it on YouTube using pywhatkit.
    Example commands: 'play Believer', 'play Bohemian Rhapsody on youtube'.
    """
    if not command:
        return "What song would you like me to play?"

    # Strip trigger words like 'play', 'song', 'on youtube'
    song = re.sub(
        r"^(play\s+song|play\s+music|play\s+on\s+youtube|play)(\s+|$)",
        "",
        command.strip(),
        flags=re.IGNORECASE,
    ).strip()
    song = re.sub(r"\b(on youtube|on music|song|video)\b", "", song, flags=re.IGNORECASE).strip()

    if not song:
        return "What song would you like me to play?"

    try:
        pywhatkit.playonyt(song)
        return f"Playing {song.title()} on YouTube."
    except Exception as e:
        return f"Sorry, I couldn't play {song}: {e}"
