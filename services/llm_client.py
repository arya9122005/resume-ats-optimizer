"""
The ONLY file that talks to Gemini. Everything else just calls call_gemini_json().
Keeping it in one place means switching AI providers later only touches this file.

How a request works:
  1. Build a list of models to try: your main model first, then the backups.
  2. Try each model. If one is busy (503), out of quota (429) or missing (404),
     move on to the next one.
  3. If every model failed, wait a few seconds and go through the list once more.
  4. Still failing? Raise an LLMError with a plain-English message.
"""
import json
import re
import time

from google import genai
from google.genai import errors, types

import config


class LLMError(Exception):
    """An error with a message that is safe and clear enough to show to the user."""

    def __init__(self, message, status_code=502, kind="other"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.kind = kind   # "quota", "busy", "not_found", "format" or "other"


class _BadReply(Exception):
    """Gemini answered, but not with usable JSON."""


_client = None


def _get_client():
    """Creates the Gemini client once and reuses it."""
    global _client
    if not config.GEMINI_API_KEY:
        raise LLMError("GEMINI_API_KEY is missing. Add it to your .env file and restart the app.", 500)
    if _client is None:
        _client = genai.Client(
            api_key=config.GEMINI_API_KEY,
            http_options=types.HttpOptions(timeout=config.GEMINI_TIMEOUT_SECONDS * 1000),  # milliseconds
        )
    return _client


def _model_chain():
    """Main model first, then the backups. No duplicates, and any 'models/' prefix is removed."""
    chain = []
    for name in [config.GEMINI_MODEL] + config.GEMINI_FALLBACK_MODELS:
        name = name.strip()
        if name.startswith("models/"):
            name = name[len("models/"):]
        if name and name not in chain:
            chain.append(name)
    return chain


def parse_json_reply(text):
    """Turns Gemini's text into a Python dict. Raises _BadReply if it can't."""
    if not text:
        raise _BadReply()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())  # remove ``` fences if present
    try:
        data = json.loads(cleaned)
    except ValueError:
        raise _BadReply()
    if not isinstance(data, dict):
        raise _BadReply()
    return data


def _is_key_problem(err):
    """True if the API key itself is the problem. Trying other models can't fix that."""
    code = getattr(err, "code", None)
    detail = str(getattr(err, "message", "") or "").lower()
    return code in (401, 403) or (code == 400 and "api key" in detail)


def _explain_api_error(err):
    """Turns a Gemini API error into a plain-English LLMError."""
    code = getattr(err, "code", None)

    if _is_key_problem(err):
        return LLMError("Gemini rejected your API key. Check GEMINI_API_KEY in your .env file.", 502)
    if code == 404:
        return LLMError("A Gemini model was not found.", 502, "not_found")
    if code == 429:
        return LLMError("Gemini rate limit or free quota reached. Wait a minute and try again.", 429, "quota")
    if code in (500, 502, 503, 504):
        return LLMError("Gemini is very busy right now. Please try again in a minute.", 503, "busy")
    return LLMError("Gemini could not process the request. Please try again.", 502)


def _most_useful(problems):
    """When every model failed, pick the message that tells the user the most."""
    kinds = [p.kind for p in problems]
    for wanted in ("quota", "busy"):
        if wanted in kinds:
            return problems[kinds.index(wanted)]
    if kinds and all(k == "not_found" for k in kinds):
        return LLMError(
            "None of the configured Gemini models are available to you. "
            "Set GEMINI_MODEL in .env to a current model name (see ai.google.dev/gemini-api/docs/models).",
            502, "not_found",
        )
    return problems[-1] if problems else LLMError("Something went wrong while contacting Gemini.")


def _debug(model, err):
    """Prints the raw Gemini error in the terminal when GEMINI_DEBUG=true (never shown to users)."""
    if config.DEBUG_LLM:
        print(f"DEBUG Gemini ({model}): {getattr(err, 'code', '')} {getattr(err, 'status', '')} {getattr(err, 'message', '')}")


def call_gemini_json(system_prompt, user_prompt):
    """
    Sends one prompt to Gemini and returns its answer as a dict.
    Raises LLMError (with a friendly message) if anything goes wrong.
    """
    client = _get_client()
    chain = _model_chain()
    problems = []

    for round_number in range(1, config.GEMINI_MAX_ROUNDS + 1):
        for model in chain:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,       # the shared rules (prompts/system.py)
                        response_mime_type="application/json",  # asks Gemini for JSON only
                    ),
                )
                return parse_json_reply(response.text)

            except errors.APIError as err:
                _debug(model, err)
                problem = _explain_api_error(err)
                if _is_key_problem(err):
                    raise problem            # a different model won't fix a bad key
                problems.append(problem)     # otherwise: try the next model
            except _BadReply:
                problems.append(LLMError("Gemini answered in an unexpected format. Please try again.", 502, "format"))
            except Exception:
                # no internet, timeout, etc. Other models would fail the same way.
                raise LLMError("Could not reach Gemini. Check your internet connection and try again.", 503)

        if round_number < config.GEMINI_MAX_ROUNDS:
            time.sleep(config.GEMINI_RETRY_DELAY_SECONDS)

    raise _most_useful(problems)
