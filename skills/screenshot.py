"""Screenshot skill for Mini-Alexa."""

import datetime
import os
import pyautogui

def take_screenshot(command: str = "") -> str:
    """
    Capture the screen and save the image with a timestamped filename.
    Returns a spoken confirmation message.
    """
    try:
        # Create a screenshots directory in project folder
        screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(screenshots_dir, filename)

        # Take and save screenshot
        image = pyautogui.screenshot()
        image.save(filepath)

        return f"Screenshot captured successfully and saved as {filename}."
    except Exception as e:
        return f"Failed to take screenshot: {e}"
