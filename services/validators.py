"""Checks user input before it goes anywhere near the AI."""
from config import MIN_INPUT_CHARS, MAX_INPUT_CHARS


def _check_one(text, name):
    text = text.strip()
    if not text:
        return f"Please paste your {name}."
    if len(text) < MIN_INPUT_CHARS:
        return f"Your {name} looks too short to analyze. Paste the full text."
    if len(text) > MAX_INPUT_CHARS:
        return f"Your {name} is too long (max {MAX_INPUT_CHARS} characters)."
    return None


def validate_inputs(resume_text, jd_text):
    """Returns a list of error messages. Empty list means the input is fine."""
    problems = [
        _check_one(resume_text, "resume"),
        _check_one(jd_text, "job description"),
    ]
    return [p for p in problems if p]
