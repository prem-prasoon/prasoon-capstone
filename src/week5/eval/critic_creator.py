"""src/week5/eval/critic_creator.py — Systematic prompt improvement loop."""
from __future__ import annotations

from openai import OpenAI
from src.week5.eval.judge import RUBRIC_PROMPT

client = OpenAI()

def creator(question: str, previous_critique: str = "", model: str = "gpt-4o-mini") -> str:
    user_content = f"Question: {question}"
    if previous_critique:
        user_content += f"\n\nAddress this critique:\n{previous_critique}\n\nProvide an improved answer."
    
    resp = client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": "You are the Creator. Write clear, grounded answers."},
            {"role": "user", "content": user_content},
        ],
    )
    return resp.choices[0].message.content or ""

def critic(question: str, draft: str, model: str = "gpt-4o") -> str:
    resp = client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": f"You are the Critic. Critique the draft using this rubric:\n\n{RUBRIC_PROMPT}\nState specific weaknesses and corrections."},
            {"role": "user", "content": f"Question: {question}\n\nDraft Answer:\n{draft}"},
        ],
    )
    return resp.choices[0].message.content or ""