"""Time and date skill for Mini-Alexa."""

import datetime

def get_time(command: str = "") -> str:
    """Return the current time as a natural spoken sentence."""
    now = datetime.datetime.now()
    # Format e.g.: 10:25 PM
    time_str = now.strftime("%I:%M %p").lstrip("0")
    return f"The current time is {time_str}."

def get_date(command: str = "") -> str:
    """Return the current date as a natural spoken sentence."""
    now = datetime.datetime.now()
    # Format e.g.: Sunday, October 25, 2026
    day_name = now.strftime("%A")
    month_name = now.strftime("%B")
    day_num = now.day
    year = now.year
    return f"Today is {day_name}, {month_name} {day_num}, {year}."
