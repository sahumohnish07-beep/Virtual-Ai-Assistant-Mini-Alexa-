# Mini-Alexa 🎙️

An intelligent, modular Python-based voice assistant built with **SpeechRecognition**, **pyttsx3**, **RapidFuzz**, and **OpenWeatherMap**, complete with an interactive **Tkinter GUI**, automated logging, conversational memory, and **LLM fallback integration**.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Folder Structure](#-folder-structure)
- [Prerequisites & Installation](#-prerequisites--installation)
- [Configuration (.env)](#-configuration-env)
- [Running Mini-Alexa](#-running-mini-alexa)
- [Supported Voice Commands](#-supported-voice-commands)
- [Error Handling & Logging](#-error-handling--logging)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## 🌟 Overview

**Mini-Alexa** is designed as an extensible pair-programming and personal productivity voice assistant for desktop environments (optimized for Windows). It supports dual operation modes: a rich graphical interface (GUI) featuring real-time state feedback and an animated microphone, and a lightweight terminal CLI mode.

If a command is not matched by any local skill, Mini-Alexa automatically queries an **LLM API** (Google Gemini or OpenAI) while maintaining the last **5 conversation turns** as context for natural follow-ups.

---

## ✨ Key Features

- **Dual Interaction Modes**:
  - **Tkinter GUI**: Animated pulsing microphone indicator, real-time status tracker (*Listening / Thinking / Speaking / Idle*), and scrollable color-coded chat history.
  - **Terminal Mode**: Zero-overhead CLI loop for quick headless or low-resource execution.
- **Fuzzy Intent Matching**: Powered by **RapidFuzz** to tolerate voice recognition typos, accents, and phrase variations (e.g., *"wether in Pune"* or *"tell me a jooke"*).
- **LLM Conversational Fallback**: Directly queries Gemini or OpenAI when no local skill matches, providing spoken 1–2 sentence explanations.
- **5-Turn Conversation Memory**: Maintains a FIFO sliding-window conversation history passed as context to the LLM.
- **Background Timed Reminders**: Non-blocking background threads (`threading.Thread`) that track countdowns and speak alerts upon expiry.
- **Persistent Local Productivity Tools**:
  - **To-Do List**: Voice-managed JSON list (`todo.json`) to add, view, and remove tasks.
  - **Dictated Notes**: Timestamped transcription appender (`notes.txt`).
- **Windows System Automation**:
  - Control master system volume (volume up, volume down, mute) via virtual multimedia keys.
  - Capture desktop screenshots saved with timestamps to `screenshots/`.
  - Launch applications (VS Code, Chrome, Notepad, Calculator) or web shortcuts (YouTube, Google).
- **Comprehensive Logging**: Automatically logs all incoming voice commands, matched skills, LLM requests, and assistant responses to `logs/assistant.log`.

---

## 🏗️ Architecture

```text
 +-------------------------------------------------------------------------+
 |                               Mini-Alexa                                |
 +-------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
 +------------------+                                     +------------------+
 | Terminal Mode    |                                     | Tkinter GUI      |
 | (main.py)        |                                     | (gui.py)         |
 +------------------+                                     +------------------+
         |                                                         |
         +----------------------------+----------------------------+
                                      |
                                      v
                      +-------------------------------+
                      |   Audio Input (listener.py)   |
                      |  - SpeechRecognition Engine   |
                      |  - Ambient Noise Calibration  |
                      |  - PyAudio / PyAudioWPatch    |
                      +-------------------------------+
                                      |
                                      v (Voice Transcription)
                      +-------------------------------+
                      |   Intent Router (intent.py)   |
                      |  - RapidFuzz Typo Matching    |
                      |  - 5-Turn Memory Retention    |
                      |  - logs/assistant.log Logger  |
                      +-------------------------------+
                                 |         |
               (Matched Skill)   |         |  (No Skill Match)
        +------------------------+         +-----------------------+
        |                                                          |
        v                                                          v
+-------------------------------+                         +--------------------+
| Modular Skills Package        |                         | LLM Fallback API   |
| • time_date.py (Clock/Date)   |                         | • Google Gemini    |
| • weather.py   (OpenWeather)  |                         | • OpenAI / Custom  |
| • wikipedia.py (2-Sentence)   |                         | • Memory Context   |
| • music.py     (YouTube Play) |                         +--------------------+
| • system_apps.py (App Launch) |                                  |
| • screenshot.py(Screen Grab)  |                                  |
| • volume.py    (Windows Keys) |                                  |
| • reminders.py (Daemon Timer) |                                  |
| • todo.py      (todo.json)    |                                  |
| • notes.py     (notes.txt)    |                                  |
| • jokes.py     (pyjokes)      |                                  |
+-------------------------------+                                  |
        |                                                          |
        +----------------------------+-----------------------------+
                                     |
                                     v (Response Text)
                     +-------------------------------+
                     |   Speech Output (speaker.py)  |
                     |  - pyttsx3 Offline TTS Engine |
                     |  - Configurable Rate & Volume |
                     +-------------------------------+
```

---

## 📁 Folder Structure

```text
ALEXA/
├── .env.example         # Template for environment variables and API keys
├── .gitignore           # Ignores venv, .env, logs, pycache, and user data
├── config.py            # Centralized settings loader via python-dotenv
├── gui.py               # Tkinter desktop GUI application
├── intent.py            # Intent dispatcher, rapidfuzz engine, & LLM handler
├── listener.py          # Speech recognition and microphone audio capture
├── main.py              # CLI entry point (Terminal mode by default, or --gui)
├── requirements.txt     # Python package dependencies
├── README.md            # Comprehensive project documentation
├── speaker.py           # Text-to-speech output using pyttsx3
├── logs/                # Session log files
│   └── assistant.log    # Persistent execution trace
├── screenshots/         # Directory for captured screenshot PNGs
│   └── .gitkeep
├── skills/              # Independent, modular voice skills
│   ├── __init__.py      # Package definition
│   ├── jokes.py         # Developer jokes via pyjokes
│   ├── music.py         # YouTube track search & play via pywhatkit
│   ├── notes.py         # Voice note dictation to notes.txt
│   ├── reminders.py     # Background threaded countdown timers
│   ├── screenshot.py    # Desktop screen grabber via pyautogui
│   ├── system_apps.py   # Windows app and website launcher
│   ├── time_date.py     # Natural time and date reporting
│   ├── todo.py          # Persistent task management in todo.json
│   ├── volume.py        # Windows multimedia audio key controller
│   ├── weather.py       # OpenWeatherMap live weather reports
│   └── wikipedia_search.py # 2-sentence encyclopedic summaries
├── notes.txt            # (Generated) Dictated notes with timestamps
└── todo.json            # (Generated) Active to-do list items
```

---

## 📦 Prerequisites & Installation

### 1. Prerequisites
- **Python**: Version 3.10+ (Fully tested on Python 3.14 on Windows 64-bit).
- **Hardware**: Working microphone and audio output (speakers/headphones).

### 2. Set Up Virtual Environment

Open PowerShell in the project directory:

```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell
.\venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

> [!NOTE]
> **Windows PyAudio Installation**:
> On Windows, if installing standard `pyaudio` fails due to missing C++ compilers, `PyAudioWPatch` provides pre-compiled 64-bit binary wheels. Run `pip install PyAudioWPatch`. `listener.py` includes automatic fallback imports for seamless compatibility.

---

## ⚙️ Configuration (.env)

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and fill in your desired parameters:

```ini
# Wake word to activate Mini-Alexa (e.g. jarvis, alexa)
WAKE_WORD=jarvis

# OpenWeatherMap API Key (https://openweathermap.org/api)
WEATHER_API_KEY=your_openweathermap_api_key_here
DEFAULT_CITY=Pune

# LLM Fallback Service ('nvidia', 'gemini', or 'openai')
LLM_API_KEY=your_api_key_here
LLM_PROVIDER=nvidia
LLM_MODEL=nvidia/nemotron-3.5-bolt-e4b
LLM_BASE_URL=https://integrate.api.nvidia.com/v1/chat/completions

# Speech Synthesis Audio Parameters
VOICE_RATE=175
VOICE_VOLUME=1.0
```

---

## 🚀 Running Mini-Alexa

### Quick Start (One-Click Launcher) ⚡
On Windows, simply double-click **`run.bat`** or run:

```cmd
run.bat
```
*`run.bat` automatically verifies your environment, activates `venv`, creates `.env` from template if missing, and provides a 5-second countdown defaulting to GUI mode.*

---

### Option A: Graphical User Interface (GUI) 🎨

Launch the Tkinter desktop GUI manually:


```powershell
python gui.py
# or
python main.py --gui
```

Click **"▶ Start Assistant"** to begin listening. Click **"⏹ Stop Assistant"** or say *"jarvis stop"* at any time to pause.

### Option B: Terminal Mode ⌨️

Launch the CLI assistant directly in your terminal:

```powershell
python main.py
```

---

## 🗣️ Supported Voice Commands

Activate the assistant by saying the wake word (**"jarvis"**) followed by your instruction:

| Skill | Voice Command Example | Action Performed |
| :--- | :--- | :--- |
| **Time** | *"jarvis what time is it"* | Speaks the current local time |
| **Date** | *"jarvis what is today's date"* | Speaks the weekday, month, day, and year |
| **Weather** | *"jarvis weather in Pune"* | Queries OpenWeatherMap for Pune |
| | *"jarvis what is the weather"* | Reports weather for `DEFAULT_CITY` |
| **Wikipedia** | *"jarvis who is Alan Turing"* | Reads 2-sentence summary with disambiguation support |
| **Jokes** | *"jarvis tell me a joke"* | Reads a random programming joke via `pyjokes` |
| **Music** | *"jarvis play Believer"* | Opens and plays track on YouTube via `pywhatkit` |
| **System Apps** | *"jarvis open Notepad"* | Launches Windows Notepad (`notepad.exe`) |
| | *"jarvis open VS Code"* | Launches Visual Studio Code (`code`) |
| | *"jarvis open YouTube"* | Launches YouTube in default web browser |
| **Screenshot** | *"jarvis take a screenshot"* | Saves capture to `screenshots/screenshot_<timestamp>.png` |
| **Volume** | *"jarvis volume up"* / *"volume down"* | Adjusts master Windows audio by ~10% |
| | *"jarvis mute"* | Toggles audio mute |
| **Reminders** | *"jarvis remind me to drink water in 10 minutes"* | Schedules daemon thread timer and speaks alert when due |
| **To-Do: Add** | *"jarvis add buy milk to my todo list"* | Appends item to `todo.json` |
| **To-Do: List**| *"jarvis show my todo list"* | Lists all pending items with numbered index |
| **To-Do: Remove**| *"jarvis remove task 1"* | Removes item from `todo.json` |
| **Notes** | *"jarvis take a note buy birthday gift"* | Appends timestamped dictation to `notes.txt` |
| **LLM Fallback**| *"jarvis why do flamingos stand on one leg?"* | Answers via Gemini/OpenAI with conversation memory |
| **Quit** | *"jarvis stop"* / *"jarvis exit"* | Quits the assistant cleanly |

---

## 🛡️ Error Handling & Logging

- **Resilient Execution**: Every skill call, web request, and TTS action is isolated within localized `try...except` blocks. If an external service is unavailable, Mini-Alexa responds with a friendly spoken message without terminating the process.
- **Trace Logs**: All events are logged to [logs/assistant.log](file:///c:/Users/Mohnish%20Sahu/OneDrive/Desktop/ALEXA/logs/assistant.log) with timestamps and log levels (`INFO`, `WARNING`, `ERROR`).
- **Network Resilience**: Handles offline internet conditions gracefully for weather, Wikipedia, and LLM requests.

---

## 🔮 Future Improvements

1. **Wake-Word Engine Upgrade**: Transition from phrase-matching to an embedded offline wake-word detector such as **Porcupine** or **openWakeWord** for zero-latency, always-on activation.
2. **Local LLM Inference**: Integrate offline models using **Ollama** or **llama.cpp** (e.g. Llama 3.2 1B / Phi-3) for fully private, air-gapped conversational intelligence.
3. **Voice Biometrics**: User identification to recognize distinct speakers and tailor reminders/tasks per user profile.
4. **Calendar Integration**: Google Calendar and Outlook API skills to manage schedules, view upcoming meetings, and create events.
5. **Smart Home Integration**: Home Assistant or Philips Hue integration to toggle lights and smart plugs by voice.
6. **Customizable Voice Models**: Support for neural TTS engines like **ElevenLabs** or **Edge-TTS** for human-grade vocal inflection.

---

## 📄 License

This project is licensed under the MIT License - feel free to customize and expand it for personal or educational use.
