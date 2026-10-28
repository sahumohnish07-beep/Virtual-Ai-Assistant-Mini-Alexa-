"""Jokes skill for Mini-Alexa using pyjokes."""

import pyjokes

def tell_joke(command: str = "") -> str:
    """Return a random programmer or neutral joke using pyjokes."""
    try:
        joke = pyjokes.get_joke()
        return joke
    except Exception as e:
        return "Why don't scientists trust atoms? Because they make up everything!"
