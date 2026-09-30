"""Central place for settings. Secrets come from environment variables, never from the code."""
import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file if it exists

USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

# --- Gemini ---
# --- Gemini ---

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

GEMINI_FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash-lite"
    ).split(",")
    if model.strip()
]

GEMINI_MAX_ROUNDS = 2

DEBUG_LLM = os.getenv("GEMINI_DEBUG", "false").lower() == "true"

GEMINI_TEMPERATURE = 0.2
GEMINI_TIMEOUT_SECONDS = 60
GEMINI_MAX_ATTEMPTS = 2

# --- Input limits ---
MIN_INPUT_CHARS = 30      # too short to analyze
MAX_INPUT_CHARS = 15000   # keeps prompts (and costs) reasonable
