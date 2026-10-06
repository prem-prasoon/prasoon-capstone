"""
src/week5/eval/judge.py — Rubric-based LLM-as-judge scoring.
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL", None)

if base_url:
    client = OpenAI(api_key=api_key, base_url=base_url)
else:
    client = OpenAI(api_key=api_key)

RUBRIC_PROMPT = """Evaluate the candidate answer against the ideal reference answer on three dimensions:

ACCURACY (1-4)
  4 = completely correct, with no subtle substitutions, conflations, or hedges that mislead
  3 = mostly correct; one minor inaccuracy that wouldn't mislead
  2 = partially correct; contains at least one substitution or conflation that would mislead
  1 = incorrect; main claim is false or unsupported

GROUNDEDNESS (1-4)
  4 = every claim traces strictly to the reference context without extraneous invention
  3 = mostly grounded with minor unsupported stylistic details
  2 = mix of grounded and unverified claims
  1 = substantially fabricated or hallucinated

FORMAT (1-4)
  4 = clear, appropriately concise, well-structured
  3 = clear but slightly verbose or terse
  2 = confusing structure or improper length
  1 = badly formatted, unreadable
"""

class JudgeScore(BaseModel):
    accuracy: int = Field(ge=1, le=4)
    groundedness: int = Field(ge=1, le=4)
    format: int = Field(ge=1, le=4)
    reasoning: str = Field(min_length=10, max_length=600)

def judge_one(question: str, candidate: str, ideal: str, model: str = "gpt-4o") -> JudgeScore:
    resp = client.beta.chat.completions.parse(
        model=model,
        temperature=0.0,
        response_format=JudgeScore,
        messages=[
            {"role": "system", "content": f"You are a strict evaluation judge.\n\n{RUBRIC_PROMPT}"},
            {"role": "user", "content": f"Question: {question}\n\nIdeal Answer:\n{ideal}\n\nCandidate Answer:\n{candidate}"},
        ],
    )
    return resp.choices[0].message.parsed