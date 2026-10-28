"""Volume control skill for Mini-Alexa on Windows."""

import pyautogui

def control_volume(command: str) -> str:
    """
    Control system audio volume (up, down, mute) using Windows multimedia keys.
    """
    if not command:
        return "Would you like me to increase, decrease, or mute the volume?"

    cmd_lower = command.lower()

    try:
        if any(phrase in cmd_lower for phrase in ["volume up", "increase volume", "raise volume", "louder", "turn up"]):
            # Press volume up key 5 times (~10% increase)
            pyautogui.press("volumeup", presses=5)
            return "Volume increased."

        elif any(phrase in cmd_lower for phrase in ["volume down", "decrease volume", "lower volume", "quieter", "turn down"]):
            # Press volume down key 5 times (~10% decrease)
            pyautogui.press("volumedown", presses=5)
            return "Volume decreased."

        elif any(phrase in cmd_lower for phrase in ["mute", "unmute", "silence"]):
            pyautogui.press("volumemute")
            return "Volume muted."

        else:
            return "You can say volume up, volume down, or mute."
    except Exception as e:
        return f"Could not adjust volume: {e}"
