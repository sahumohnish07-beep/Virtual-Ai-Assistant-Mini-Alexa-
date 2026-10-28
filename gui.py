"""Mini-Alexa GUI: Tkinter-based graphical interface with status indicator and chat log."""

import datetime
import math
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext

import config
from listener import listen
from speaker import speak
from intent import handle

# Color Palette (Catppuccin Mocha inspired dark theme)
BG_COLOR = "#1e1e2e"
SURFACE_COLOR = "#252538"
INPUT_BG = "#181825"
TEXT_COLOR = "#cdd6f4"
MUTED_TEXT = "#6c7086"
USER_COLOR = "#89b4fa"      # Blue
ALEXA_COLOR = "#a6e3a1"     # Green
SYSTEM_COLOR = "#f9e2af"    # Warm Yellow

STATUS_COLORS = {
    "Idle": "#6c7086",
    "Listening...": "#f38ba8",   # Coral Red / Pink
    "Thinking...": "#fab387",    # Orange / Amber
    "Speaking...": "#a6e3a1",    # Emerald Green
}

class AlexaGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Mini-Alexa Voice Assistant")
        self.root.geometry("540x700")
        self.root.minsize(480, 620)
        self.root.configure(bg=BG_COLOR)

        # Threading state
        self.is_running = False
        self.stop_event = threading.Event()
        self.worker_thread = None
        self.msg_queue = queue.Queue()

        # Animation state
        self.current_status = "Idle"
        self.pulse_phase = 0.0

        # Build UI layout
        self._build_header()
        self._build_mic_indicator()
        self._build_chat_log()
        self._build_controls()

        # Start queue processing and animation loop
        self.root.after(40, self._process_queue)
        self.root.after(40, self._animate_mic)

        # Clean shutdown handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_header(self):
        """Top banner showing title and wake word reminder."""
        header_frame = tk.Frame(self.root, bg=BG_COLOR)
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 5))

        title_lbl = tk.Label(
            header_frame,
            text="MINI-ALEXA",
            font=("Segoe UI", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        title_lbl.pack()

        subtitle = f"Wake Word: '{config.WAKE_WORD}' • Say 'stop' or 'exit' to quit"
        sub_lbl = tk.Label(
            header_frame,
            text=subtitle,
            font=("Segoe UI", 9),
            bg=BG_COLOR,
            fg=MUTED_TEXT,
        )
        sub_lbl.pack(pady=(2, 0))

    def _build_mic_indicator(self):
        """Canvas indicator that pulses during listening and reflects state."""
        mic_frame = tk.Frame(self.root, bg=BG_COLOR)
        mic_frame.pack(fill=tk.X, padx=20, pady=10)

        # Pulsing circle canvas
        self.canvas_size = 110
        self.canvas = tk.Canvas(
            mic_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=BG_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()

        # Dynamic Status text label
        self.status_lbl = tk.Label(
            mic_frame,
            text="Idle",
            font=("Segoe UI", 15, "bold"),
            bg=BG_COLOR,
            fg=STATUS_COLORS["Idle"],
        )
        self.status_lbl.pack(pady=(6, 0))

    def _build_chat_log(self):
        """Scrollable conversation history window."""
        chat_frame = tk.Frame(self.root, bg=BG_COLOR)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        lbl = tk.Label(
            chat_frame,
            text="Conversation Log",
            font=("Segoe UI", 10, "bold"),
            bg=BG_COLOR,
            fg=MUTED_TEXT,
            anchor="w",
        )
        lbl.pack(fill=tk.X, pady=(0, 4))

        self.chat_box = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg=INPUT_BG,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10),
            padx=12,
            pady=10,
            borderwidth=1,
            relief=tk.FLAT,
            state=tk.DISABLED,
        )
        self.chat_box.pack(fill=tk.BOTH, expand=True)

        # Configure style tags
        self.chat_box.tag_config("user_tag", foreground=USER_COLOR, font=("Segoe UI", 10, "bold"))
        self.chat_box.tag_config("alexa_tag", foreground=ALEXA_COLOR, font=("Segoe UI", 10, "bold"))
        self.chat_box.tag_config("system_tag", foreground=SYSTEM_COLOR, font=("Segoe UI", 9, "italic"))
        self.chat_box.tag_config("time_tag", foreground=MUTED_TEXT, font=("Segoe UI", 8))
        self.chat_box.tag_config("text_body", foreground=TEXT_COLOR, font=("Segoe UI", 10))

        self.append_message("system", "Mini-Alexa is ready. Click 'Start Assistant' to begin listening.")

    def _build_controls(self):
        """Start and Stop action buttons."""
        ctrl_frame = tk.Frame(self.root, bg=BG_COLOR)
        ctrl_frame.pack(fill=tk.X, padx=20, pady=(5, 18))

        self.start_btn = tk.Button(
            ctrl_frame,
            text="▶ Start Assistant",
            font=("Segoe UI", 11, "bold"),
            bg="#a6e3a1",
            fg="#11111b",
            activebackground="#94e2d5",
            activeforeground="#11111b",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.start_assistant,
        )
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        self.stop_btn = tk.Button(
            ctrl_frame,
            text="⏹ Stop Assistant",
            font=("Segoe UI", 11, "bold"),
            bg="#f38ba8",
            fg="#11111b",
            activebackground="#eba0ac",
            activeforeground="#11111b",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED,
            command=self.stop_assistant,
        )
        self.stop_btn.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(6, 0))

    def _animate_mic(self):
        """Draw animated pulsing rings on Canvas according to current assistant status."""
        self.canvas.delete("all")
        cx = self.canvas_size / 2
        cy = self.canvas_size / 2
        base_r = 26

        self.pulse_phase = (self.pulse_phase + 0.16) % (2 * math.pi)

        if self.current_status == "Listening...":
            # Pulsing expanding ripple rings
            wave1 = base_r + 8 + 8 * math.sin(self.pulse_phase)
            wave2 = base_r + 16 + 12 * math.sin(self.pulse_phase - 0.7)

            self.canvas.create_oval(
                cx - wave2, cy - wave2, cx + wave2, cy + wave2,
                outline="#45475a", width=2
            )
            self.canvas.create_oval(
                cx - wave1, cy - wave1, cx + wave1, cy + wave1,
                outline=STATUS_COLORS["Listening..."], width=2
            )
            center_color = "#f38ba8"

        elif self.current_status == "Thinking...":
            # Breathing pulse ring
            wave = base_r + 6 + 4 * math.sin(self.pulse_phase * 1.5)
            self.canvas.create_oval(
                cx - wave, cy - wave, cx + wave, cy + wave,
                outline=STATUS_COLORS["Thinking..."], width=2
            )
            center_color = "#fab387"

        elif self.current_status == "Speaking...":
            # Sound wave ring
            wave = base_r + 7 + 6 * abs(math.sin(self.pulse_phase * 2))
            self.canvas.create_oval(
                cx - wave, cy - wave, cx + wave, cy + wave,
                outline=STATUS_COLORS["Speaking..."], width=2
            )
            center_color = "#a6e3a1"

        else:
            # Idle ring
            self.canvas.create_oval(
                cx - base_r - 4, cy - base_r - 4, cx + base_r + 4, cy + base_r + 4,
                outline="#313244", width=2
            )
            center_color = "#313244"

        # Center core circle
        self.canvas.create_oval(
            cx - base_r, cy - base_r, cx + base_r, cy + base_r,
            fill=center_color, outline="",
        )

        # Microphone icon in center
        mic_symbol = "🎙"
        icon_fg = "#11111b" if self.current_status != "Idle" else "#cdd6f4"
        self.canvas.create_text(
            cx, cy,
            text=mic_symbol,
            font=("Segoe UI Emoji", 20),
            fill=icon_fg,
        )

        # Loop next animation frame
        self.root.after(40, self._animate_mic)

    def _set_status(self, status: str):
        """Update current status text and theme color."""
        self.current_status = status
        color = STATUS_COLORS.get(status, TEXT_COLOR)
        self.status_lbl.config(text=status, fg=color)

    def append_message(self, sender: str, message: str):
        """Append formatted message to the scrolling chat window."""
        self.chat_box.config(state=tk.NORMAL)
        t_now = datetime.datetime.now().strftime("%I:%M %p")

        if sender == "user":
            self.chat_box.insert(tk.END, f"[{t_now}] ", "time_tag")
            self.chat_box.insert(tk.END, "You: ", "user_tag")
            self.chat_box.insert(tk.END, f"{message}\n\n", "text_body")
        elif sender == "alexa":
            self.chat_box.insert(tk.END, f"[{t_now}] ", "time_tag")
            self.chat_box.insert(tk.END, "Mini-Alexa: ", "alexa_tag")
            self.chat_box.insert(tk.END, f"{message}\n\n", "text_body")
        else:
            self.chat_box.insert(tk.END, f"[{t_now}] • {message}\n\n", "system_tag")

        self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)

    def _process_queue(self):
        """Check the thread-safe message queue and update GUI widgets."""
        try:
            while not self.msg_queue.empty():
                msg_type, payload = self.msg_queue.get_nowait()
                if msg_type == "status":
                    self._set_status(payload)
                elif msg_type == "chat":
                    sender, text = payload
                    self.append_message(sender, text)
        except Exception:
            pass
        finally:
            self.root.after(40, self._process_queue)

    def start_assistant(self):
        """Start the background voice assistant thread."""
        if self.is_running:
            return

        self.is_running = True
        self.stop_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        self.append_message("system", "Assistant activated. Listening for commands...")
        self._set_status("Listening...")

        self.worker_thread = threading.Thread(target=self._assistant_loop, daemon=True)
        self.worker_thread.start()

    def stop_assistant(self):
        """Stop the background voice assistant loop."""
        if not self.is_running:
            return

        self.is_running = False
        self.stop_event.set()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        self._set_status("Idle")
        self.append_message("system", "Assistant stopped.")

    def _assistant_loop(self):
        """Background worker thread running the continuous listening loop."""
        wake_word = config.WAKE_WORD.lower()

        # Initial spoken greeting
        self.msg_queue.put(("status", "Speaking..."))
        speak(f"Mini-Alexa is ready. Say {wake_word} to start.")

        while not self.stop_event.is_set():
            try:
                self.msg_queue.put(("status", "Listening..."))
                heard_text = listen()

                if self.stop_event.is_set():
                    break

                if not heard_text:
                    continue

                # Check for explicit stop keyword
                if heard_text in ["stop", "exit", "quit", "goodbye"]:
                    self.msg_queue.put(("chat", ("user", heard_text)))
                    self.msg_queue.put(("status", "Speaking..."))
                    self.msg_queue.put(("chat", ("alexa", "Goodbye! Have a nice day.")))
                    speak("Goodbye! Have a nice day.")
                    self.root.after(0, self.stop_assistant)
                    break

                # Wake word detection or direct command in GUI mode
                command = ""
                if wake_word in heard_text:
                    command = heard_text.replace(wake_word, "").strip()
                    if not command:
                        self.msg_queue.put(("status", "Speaking..."))
                        speak("Yes? How can I help you?")
                        self.msg_queue.put(("status", "Listening..."))
                        command = listen()
                else:
                    # Allow direct spoken instruction in GUI mode
                    command = heard_text.strip()

                if not command or self.stop_event.is_set():
                    continue

                if command in ["stop", "exit", "quit", "bye", "goodbye"]:
                    self.msg_queue.put(("chat", ("user", command)))
                    self.msg_queue.put(("status", "Speaking..."))
                    self.msg_queue.put(("chat", ("alexa", "Goodbye! Have a nice day.")))
                    speak("Goodbye! Have a nice day.")
                    self.root.after(0, self.stop_assistant)
                    break

                # 1. User command received
                self.msg_queue.put(("chat", ("user", command)))

                # 2. Thinking / Intent Routing
                self.msg_queue.put(("status", "Thinking..."))
                reply = handle(command)

                # 3. Speaking response
                self.msg_queue.put(("status", "Speaking..."))
                self.msg_queue.put(("chat", ("alexa", reply)))
                speak(reply)

            except Exception as e:
                self.msg_queue.put(("chat", ("system", f"Encountered error: {e}")))

        self.msg_queue.put(("status", "Idle"))

    def on_close(self):
        """Clean shutdown when closing the GUI window."""
        self.stop_assistant()
        self.root.destroy()

def launch_gui():
    """Launch the Tkinter GUI."""
    root = tk.Tk()
    AlexaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
