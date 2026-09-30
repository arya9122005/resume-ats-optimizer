"""
DEMO MODE ONLY.
Not AI. It just checks a fixed list of common skills against both texts,
so we can build and test the UI before connecting Gemini (Step 4).
The result has the same shape the real AI prompts will return later.
"""
import re

SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "html", "css",
    "flask", "django", "react", "node.js", "sql", "mysql", "postgresql",
    "mongodb", "git", "github", "docker", "aws", "rest api", "linux",
    "machine learning", "data structures", "agile",
]


def find_skills(text):
    """Returns the set of known skills that appear in the text."""
    text = text.lower()
    found = set()
    for skill in SKILLS:
        # (?<!\w) and (?!\w) act like word boundaries and also work for "c++"
        if re.search(rf"(?<!\w){re.escape(skill)}s?(?!\w)", text):
            found.add(skill)
    return found


def mock_analysis(resume_text, jd_text):
    resume_skills = find_skills(resume_text)
    jd_skills = find_skills(jd_text)

    matched = sorted(jd_skills & resume_skills)
    missing = sorted(jd_skills - resume_skills)

    if not jd_skills:
        fit = "unknown"
    else:
        ratio = len(matched) / len(jd_skills)
        fit = "strong" if ratio >= 0.75 else "moderate" if ratio >= 0.4 else "weak"

    return {
        "mode": "demo",
        "comparison": {
            "overall_fit": fit,
            "matches": [
                {"requirement": s, "evidence": "Found in resume text", "status": "explicit"}
                for s in matched
            ],
            "gaps": [
                {"requirement": s, "status": "not_found", "note": "Not found in resume text"}
                for s in missing
            ],
            "strengths": (
                [f"{len(matched)} skill(s) from the job description appear in your resume."]
                if matched else []
            ),
            "improvement_areas": (
                [f"Check whether you have real experience with: {', '.join(missing)}."]
                if missing else []
            ),
        },
        "keywords": {
            "found": [{"keyword": s, "category": "technical_skills", "status": "explicit"} for s in matched],
            "missing": [{"keyword": s, "category": "technical_skills", "priority": "medium"} for s in missing],
        },
    }
