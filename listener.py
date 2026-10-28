"""Speech recognition module for Mini-Alexa."""

import sys

# Ensure PyAudio or PyAudioWPatch is accessible for microphone audio capture
try:
    import pyaudio  # noqa: F401
except ImportError:
    try:
        import pyaudiowpatch as pyaudio
        sys.modules["pyaudio"] = pyaudio
    except ImportError:
        pass

import speech_recognition as sr

recognizer = sr.Recognizer()

def listen() -> str:
    """
    Use SpeechRecognition with the microphone to capture speech input.
    Calls adjust_for_ambient_noise and returns recognized text in lowercase.
    Handles UnknownValueError, RequestError, and timeouts by returning an empty string.
    """
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio)
            return text.lower()
    except (sr.WaitTimeoutError, TimeoutError):
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return ""
    except Exception as e:
        print(f"Error during audio listening: {e}")
        return ""
