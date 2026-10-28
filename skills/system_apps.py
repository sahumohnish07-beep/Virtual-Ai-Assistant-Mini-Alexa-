"""System applications and web launcher skill for Mini-Alexa on Windows."""

import os
import subprocess
import webbrowser

# Dictionary mapping voice app names to executable commands, system paths, or URLs
APP_MAP = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
}

def open_app(command: str) -> str:
    """
    Open an application or website on Windows using the APP_MAP dictionary.
    Supports Chrome, VS Code, Notepad, Calculator, YouTube, and Google.
    """
    if not command:
        return "Which application or website would you like me to open?"

    cmd_clean = command.lower()

    # Find the matching application or website in APP_MAP
    target = None
    matched_name = None

    # Check longer names first to avoid partial matches
    for app_name in sorted(APP_MAP.keys(), key=len, reverse=True):
        if app_name in cmd_clean:
            target = APP_MAP[app_name]
            matched_name = app_name
            break

    if not target:
        return "Sorry, I couldn't find that application. You can ask me to open Chrome, VS Code, Notepad, Calculator, YouTube, or Google."

    try:
        # If target is a URL, open in the browser
        if target.startswith("http://") or target.startswith("https://"):
            webbrowser.open(target)
            return f"Opening {matched_name.title()}."

        # Otherwise, launch the Windows executable or command
        try:
            os.startfile(target)
        except (FileNotFoundError, OSError):
            subprocess.Popen(f"start {target}", shell=True)

        return f"Opening {matched_name.title()}."
    except Exception as e:
        return f"Failed to open {matched_name}: {e}"
