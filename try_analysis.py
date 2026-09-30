"""
Tests the REAL Gemini analysis from the terminal (no browser needed).
Run:  python try_analysis.py
Needs GEMINI_API_KEY in your .env file.
"""
import json
import sys

from services.analyzer import run_ai_analysis
from services.llm_client import LLMError

RESUME = """Skills: Python, Flask, HTML, CSS, MySQL
Project: Library Management System - built a web app using Flask and MySQL
to manage book records. Used by 3 faculty members.
Education: B.Tech CSE, 2027"""

JOB_DESCRIPTION = """Junior Backend Developer.
Required: Python, Flask, REST APIs, SQL, Git.
Nice to have: Docker, AWS.
You will build and maintain APIs and write clean, tested code."""

try:
    result = run_ai_analysis(RESUME, JOB_DESCRIPTION)
except LLMError as err:
    print("Error:", err.message)
    sys.exit(1)

print(json.dumps(result, indent=2))
