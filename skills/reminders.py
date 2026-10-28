"""Reminder skill for Mini-Alexa to schedule reminders in background threads."""

import datetime
import re
import threading
import time
from speaker import speak

# Map common English number words to integers
WORD_TO_NUMBER = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "fifteen": 15,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
}

def _reminder_timer(delay_seconds: float, message: str):
    """Background worker that sleeps for the duration and speaks the reminder."""
    time.sleep(delay_seconds)
    speak(f"Reminder: {message}")

def set_reminder(command: str) -> str:
    """
    Parse a reminder command like 'remind me to drink water in 10 minutes',
    start a background thread timer, and speak the reminder when due.
    """
    if not command:
        return "What would you like me to remind you about, and when?"

    cmd = command.strip().lower()

    # Pattern matching: in <number|word> <seconds|minutes|hours>
    time_pattern = r"\bin\s+(\d+|[a-z]+)\s+(second|seconds|sec|secs|minute|minutes|min|mins|hour|hours|hr|hrs)\b"
    match = re.search(time_pattern, cmd, re.IGNORECASE)

    if not match:
        return "Please specify when to remind you, for example: remind me to drink water in 10 minutes."

    num_str = match.group(1).lower()
    unit_str = match.group(2).lower()

    # Convert number word or digit string to integer
    if num_str.isdigit():
        amount = int(num_str)
    elif num_str in WORD_TO_NUMBER:
        amount = WORD_TO_NUMBER[num_str]
    else:
        return f"Sorry, I could not understand the number '{num_str}'."

    # Convert unit to seconds
    if "sec" in unit_str:
        delay = amount
        unit_display = "second" if amount == 1 else "seconds"
    elif "min" in unit_str:
        delay = amount * 60
        unit_display = "minute" if amount == 1 else "minutes"
    elif "hour" in unit_str or "hr" in unit_str:
        delay = amount * 3600
        unit_display = "hour" if amount == 1 else "hours"
    else:
        delay = amount * 60
        unit_display = "minutes"

    # Extract reminder message by stripping trigger phrases and the 'in X minutes' part
    clean_msg = re.sub(time_pattern, "", cmd, flags=re.IGNORECASE)
    clean_msg = re.sub(
        r"^(remind me to|remind me that|remind me|set a reminder to|set a reminder for|reminder)\s+",
        "",
        clean_msg.strip(),
        flags=re.IGNORECASE,
    ).strip()

    if not clean_msg:
        clean_msg = "check your task"

    # Start timer in background daemon thread
    timer_thread = threading.Thread(
        target=_reminder_timer,
        args=(delay, clean_msg),
        daemon=True,
    )
    timer_thread.start()

    return f"I will remind you to {clean_msg} in {amount} {unit_display}."
