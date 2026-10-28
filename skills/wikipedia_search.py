"""Wikipedia search skill for Mini-Alexa."""

import re
import wikipedia

def search_wikipedia(command: str) -> str:
    """
    Search Wikipedia and return a 2-sentence summary.
    Handles DisambiguationError, PageError, and network failures gracefully.
    """
    if not command:
        return "What would you like me to search on Wikipedia?"

    # Strip trigger phrases to isolate the search query
    query = re.sub(
        r"^(who is|what is|tell me about|search wikipedia for|search for|wikipedia|look up)(\s+|$)",
        "",
        command.strip(),
        flags=re.IGNORECASE,
    ).strip()

    # Remove phrases like 'on wikipedia' or 'in wikipedia'
    query = re.sub(r"\b(on wikipedia|in wikipedia)\b", "", query, flags=re.IGNORECASE).strip()

    if not query:
        return "What would you like me to search on Wikipedia?"

    try:
        # Fetch 2-sentence summary
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        # Attempt to retrieve the first disambiguation candidate or give preview
        try:
            first_match = e.options[0]
            summary = wikipedia.summary(first_match, sentences=2)
            return f"Referring to {first_match}: {summary}"
        except Exception:
            preview = ", ".join(e.options[:3])
            return f"There are several topics for '{query}', including {preview}. Please be more specific."
    except wikipedia.exceptions.PageError:
        return f"Sorry, I couldn't find any Wikipedia page matching '{query}'."
    except Exception as e:
        return f"Sorry, I could not retrieve information from Wikipedia: {e}"
