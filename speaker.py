"""
Text-to-Speech (TTS) Engine for Mini-Alexa.

Utilizes pyttsx3 to synthesize speech offline with configurable voice speed and volume.
"""

import pyttsx3
import config

# Initialize the pyttsx3 TTS engine instance
try:
    engine = pyttsx3.init()
except Exception as init_err:
    print(f"Warning: Could not initialize pyttsx3 engine: {init_err}")
    engine = None

def speak(text: str):
    """
    Speak text aloud using pyttsx3 and print the text to the console.

    Parameters:
        text (str): The text message to speak and display.
    """
    if not text:
        return

    # Print the spoken text for console visibility
    print(f"Mini-Alexa: {text}")

    if not engine:
        return

    try:
        # Dynamically set voice rate and volume from config
        rate = getattr(config, "VOICE_RATE", 175)
        volume = getattr(config, "VOICE_VOLUME", 1.0)

        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)

        engine.say(text)
        engine.runAndWait()
    except Exception as err:
        print(f"TTS Speech Error: {err}")
