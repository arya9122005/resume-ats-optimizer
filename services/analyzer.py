"""
Runs the two prompts and returns the SAME response shape as demo mode,
so the frontend needs no changes.

Also "cleans" Gemini's answer. LLMs sometimes return a wrong label or a made-up quote,
so we never send raw AI output straight to the browser.
"""
import re

from prompts.system import SYSTEM_PROMPT
from prompts.compare import build_compare_prompt
from prompts.keywords import build_keywords_prompt
from services.llm_client import call_gemini_json

FITS = {"strong", "moderate", "weak", "unknown"}
CATEGORIES = {"technical_skills", "tools", "soft_skills", "domain_terms"}
PRIORITIES = {"high", "medium", "low"}


# ---------- tiny helpers ----------
def _text(value, limit=300):
    """Safe short string (handles None and wrong types)."""
    return "" if value is None else str(value).strip()[:limit]


def _dicts(value):
    """Keeps only the dict items of a list. Anything else becomes an empty list."""
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _strings(value, max_items=4):
    if not isinstance(value, list):
        return []
    return [_text(v) for v in value if _text(v)][:max_items]


def _simplify(text):
    """lowercase + only letters/digits/+/# so quotes can be compared fairly."""
    return " ".join(re.sub(r"[^a-z0-9+#]+", " ", text.lower()).split())


def _in_resume(needle, resume_simple):
    n = _simplify(needle)
    return bool(n) and f" {n} " in f" {resume_simple} "


# ---------- cleaning ----------
def clean_comparison(raw, resume_text):
    resume_simple = _simplify(resume_text)

    fit = _text(raw.get("overall_fit")).lower()
    if fit not in FITS:
        fit = "unknown"

    matches = []
    for item in _dicts(raw.get("matches")):
        requirement = _text(item.get("requirement"))
        if not requirement:
            continue

        # Guard 1: a quote that is not really in the resume is dropped
        evidence = _text(item.get("evidence"))
        if not _in_resume(evidence, resume_simple):
            evidence = ""

        # Guard 2: "explicit" must be backed by the resume. Otherwise downgrade to "inferred".
        status = _text(item.get("status")).lower()
        if status not in ("explicit", "inferred"):
            status = "inferred"
        if status == "explicit" and not (evidence or _in_resume(requirement, resume_simple)):
            status = "inferred"

        matches.append({"requirement": requirement, "evidence": evidence, "status": status})

    gaps = []
    for item in _dicts(raw.get("gaps")):
        requirement = _text(item.get("requirement"))
        if not requirement:
            continue
        status = _text(item.get("status")).lower()
        if status not in ("not_found", "unclear"):
            status = "unclear"
        gaps.append({"requirement": requirement, "status": status, "note": _text(item.get("note"))})

    return {
        "overall_fit": fit,
        "matches": matches,
        "gaps": gaps,
        "strengths": _strings(raw.get("strengths")),
        "improvement_areas": _strings(raw.get("improvement_areas")),
    }


def clean_keywords(raw, resume_text):
    resume_simple = _simplify(resume_text)

    found = []
    for item in _dicts(raw.get("found")):
        keyword = _text(item.get("keyword"), 80)
        if not keyword:
            continue
        category = _text(item.get("category")).lower()
        status = _text(item.get("status")).lower()
        if status != "explicit" or not _in_resume(keyword, resume_simple):
            status = "inferred"   # only "explicit" if the word is really in the resume
        found.append({
            "keyword": keyword,
            "category": category if category in CATEGORIES else "domain_terms",
            "status": status,
        })

    missing = []
    for item in _dicts(raw.get("missing")):
        keyword = _text(item.get("keyword"), 80)
        if not keyword:
            continue
        category = _text(item.get("category")).lower()
        priority = _text(item.get("priority")).lower()
        missing.append({
            "keyword": keyword,
            "category": category if category in CATEGORIES else "domain_terms",
            "priority": priority if priority in PRIORITIES else "medium",
        })

    return {"found": found, "missing": missing}


# ---------- main entry point ----------
def run_ai_analysis(resume_text, jd_text):
    """Two prompts -> two Gemini calls -> one combined, cleaned result."""
    comparison_raw = call_gemini_json(SYSTEM_PROMPT, build_compare_prompt(resume_text, jd_text))
    keywords_raw = call_gemini_json(SYSTEM_PROMPT, build_keywords_prompt(resume_text, jd_text))

    return {
        "mode": "ai",
        "comparison": clean_comparison(comparison_raw, resume_text),
        "keywords": clean_keywords(keywords_raw, resume_text),
    }
