"""
Prompt template 1: Resume vs Job Description comparison.

Techniques: context-based prompting (resume + JD in tagged blocks), clear step-by-step
instructions, structured output (JSON schema), constraint prompting, and one short
example (few-shot) so the format stays consistent.

Placeholders <<RESUME_TEXT>> and <<JD_TEXT>> are swapped in by build_compare_prompt().
"""

COMPARE_TEMPLATE = """\
TASK
Compare the resume with the job description.

<resume>
<<RESUME_TEXT>>
</resume>

<job_description>
<<JD_TEXT>>
</job_description>

STEPS
1. List the 5 to 12 most important requirements in the job description (skills, tools, \
qualifications, responsibilities). Treat "required" items as more important than "nice to have".
2. For each requirement, look for evidence in the resume.
3. Requirements with clear evidence go in "matches". Requirements with no or weak \
evidence go in "gaps".
4. Set "overall_fit":
   - "strong": most important requirements are clearly shown.
   - "moderate": about half are clearly shown.
   - "weak": few are shown.
   - "unknown": the job description has no clear requirements to compare against.
5. Write up to 4 "strengths" and up to 4 "improvement_areas". Each must point to something \
specific in the resume or job description. Improvement areas must be things the candidate \
can fix by clarifying or verifying real experience, never by inventing any.

OUTPUT SCHEMA
{
  "overall_fit": "strong" | "moderate" | "weak" | "unknown",
  "matches": [
    {"requirement": "short name", "evidence": "exact short quote from the resume", "status": "explicit" | "inferred"}
  ],
  "gaps": [
    {"requirement": "short name", "status": "not_found" | "unclear", "note": "one short sentence"}
  ],
  "strengths": ["..."],
  "improvement_areas": ["..."]
}

EXAMPLE (for format only. Do not reuse its content)
Resume: "Skills: Python, Flask, MySQL. Built a library web app using Flask and MySQL."
Job description: "Required: Python, Flask, SQL, Git."
Output:
{
  "overall_fit": "moderate",
  "matches": [
    {"requirement": "Python", "evidence": "Skills: Python", "status": "explicit"},
    {"requirement": "Flask", "evidence": "Skills: Python, Flask", "status": "explicit"},
    {"requirement": "SQL", "evidence": "MySQL", "status": "inferred"}
  ],
  "gaps": [
    {"requirement": "Git", "status": "not_found", "note": "Version control is not mentioned."}
  ],
  "strengths": ["The library web app shows Flask and MySQL used together."],
  "improvement_areas": ["Mention Git only if you have actually used it."]
}

Now produce the JSON for the resume and job description above.
"""


def build_compare_prompt(resume_text, jd_text):
    prompt = COMPARE_TEMPLATE.replace("<<RESUME_TEXT>>", resume_text.strip())
    return prompt.replace("<<JD_TEXT>>", jd_text.strip())
