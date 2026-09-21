"""mp1/prompts.py - Four prompting strategies for job metadata extraction."""

# 1. Zero-shot: Direct task prompt without edge-case guidance
ZERO_SHOT_PROMPT = """Extract the company, role, and years of experience required from this job posting.
Return only a JSON object with keys: "company", "role", "years_experience_required".

Job Posting:
{snippet}
"""

# 2. Few-shot: Includes explicit examples showing both numeric and entry-level cases
FEW_SHOT_PROMPT = """Extract company, role, and years_experience_required from the job posting as JSON.

Example 1:
Posting: "Infosys is hiring a Systems Engineer. Candidates must have at least 2 years of experience."
Output: {{"company": "Infosys", "role": "Systems Engineer", "years_experience_required": 2}}

Example 2:
Posting: "Wipro is seeking Associate Analysts. Freshers welcome, no prior experience needed."
Output: {{"company": "Wipro", "role": "Associate Analyst", "years_experience_required": null}}

Job Posting:
{snippet}
Output:"""

# 3. Structured: Role definition with explicit output constraints
STRUCTURED_ROLE_PROMPT = """You are an expert HR recruiter and parser. Extract the role, company, and minimum years of experience from the job snippet.

Output strictly as a valid JSON object matching this schema:
{{
  "company": "string or null",
  "role": "string or null",
  "years_experience_required": "integer or null"
}}

Guidelines:
- If no experience requirement is mentioned, set years_experience_required to null.
- If fresh graduates / entry-level is explicitly mentioned with no prior experience needed, set it to 0.
- Return raw JSON only with no markdown formatting.

Job Posting:
{snippet}
"""

# 4. Chain-of-thought: Explicit extraction reasoning prior to JSON output
COT_PROMPT = """Analyze the job posting step by step:
1. Identify the company name.
2. Identify the role title.
3. Identify the minimum years of experience required (integer, or null if none/freshers).

At the very end, output the result in a valid JSON block enclosed in ```json ... ``` with the exact keys:
"company", "role", and "years_experience_required".

Job Posting:
{snippet}
"""