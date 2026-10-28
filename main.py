"""Mini-Alexa: Main voice assistant application (Terminal & GUI Launcher)."""

import sys
import config
from listener import listen
from speaker import speak
from intent import handle

def main():
    """Terminal loop: wait for wake word, take command, route to intent handler, and speak result."""
    wake_word = config.WAKE_WORD.lower()
    print("=" * 55)
    print("Mini-Alexa Voice Assistant is running (Terminal Mode)!")
    print(f"Wake word: '{wake_word}' (say '{wake_word}' to activate)")
    print("Say 'stop' or 'exit' at any time to quit.")
    print("Tip: Run 'python gui.py' or 'python main.py --gui' for the GUI.")
    print("=" * 55)
    speak(f"Mini-Alexa is ready. Say {wake_word} to start.")

    while True:
        try:
            # 1. Wait for speech input
            heard_text = listen()
            if not heard_text:
                continue

            # Check if user directly asked to quit
            if heard_text in ["stop", "exit", "quit", "goodbye"]:
                speak("Goodbye! Have a nice day.")
                break

            # 2. Check for the wake word
            if wake_word in heard_text:
                # Extract command following the wake word
                command = heard_text.replace(wake_word, "").strip()

                # If only the wake word was spoken, prompt for command
                if not command:
                    speak("Yes? How can I help you?")
                    command = listen()

                if not command:
                    continue

                # Check if command is an exit request
                if command in ["stop", "exit", "quit", "bye", "goodbye"]:
                    speak("Goodbye! Have a nice day.")
                    break

                # 3. Pass command to handle() and speak the result
                response = handle(command)
                if response:
                    speak(response)

        except KeyboardInterrupt:
            print("\nExiting Mini-Alexa...")
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    if "--gui" in sys.argv:
        from gui import launch_gui
        launch_gui()
    else:
        main()
