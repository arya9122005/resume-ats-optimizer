"""
Prompt template 2: Skill and keyword analysis.

Same building blocks as the comparison prompt, but a different job: pull keywords out of
the job description, then check which ones the resume really contains.
"""

KEYWORDS_TEMPLATE = """\
TASK
Find the important keywords in the job description and check which ones appear in the resume.

<resume>
<<RESUME_TEXT>>
</resume>

<job_description>
<<JD_TEXT>>
</job_description>

STEPS
1. Pick 8 to 20 keywords or short phrases from the job description. Use the job description's \
own wording. Include technical skills, tools, and domain terms. Include a soft skill only if \
the job description clearly stresses it. Skip generic words such as "team" or "work".
2. Give each keyword a category: "technical_skills", "tools", "soft_skills", or "domain_terms".
3. Check the resume for each keyword:
   - The exact term or an obvious variant is written -> "found" with status "explicit".
   - It is strongly implied but not written -> "found" with status "inferred".
   - There is no evidence -> "missing".
4. For each missing keyword set "priority":
   - "high": the job description says required, must, or repeats it.
   - "medium": listed without emphasis.
   - "low": described as nice to have or preferred.
5. List each keyword once. Never mark a keyword as found without evidence in the resume.

OUTPUT SCHEMA
{
  "found": [
    {"keyword": "...", "category": "technical_skills" | "tools" | "soft_skills" | "domain_terms", "status": "explicit" | "inferred"}
  ],
  "missing": [
    {"keyword": "...", "category": "technical_skills" | "tools" | "soft_skills" | "domain_terms", "priority": "high" | "medium" | "low"}
  ]
}

EXAMPLE (for format only. Do not reuse its content)
Resume: "Skills: Python, Flask, MySQL."
Job description: "Required: Python, SQL, Git. Nice to have: Docker."
Output:
{
  "found": [
    {"keyword": "Python", "category": "technical_skills", "status": "explicit"},
    {"keyword": "SQL", "category": "technical_skills", "status": "inferred"}
  ],
  "missing": [
    {"keyword": "Git", "category": "tools", "priority": "high"},
    {"keyword": "Docker", "category": "tools", "priority": "low"}
  ]
}

Now produce the JSON for the resume and job description above.
"""


def build_keywords_prompt(resume_text, jd_text):
    prompt = KEYWORDS_TEMPLATE.replace("<<RESUME_TEXT>>", resume_text.strip())
    return prompt.replace("<<JD_TEXT>>", jd_text.strip())
