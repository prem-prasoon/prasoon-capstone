"""src/week5/eval/pairwise.py — Pairwise comparison with position debiasing."""
from __future__ import annotations

import random
from openai import OpenAI
from pydantic import BaseModel, Field

class PairwiseVerdict(BaseModel):
    winner: str = Field(pattern="^[AB]$")
    reasoning: str = Field(min_length=10, max_length=500)

client = OpenAI()

def pairwise_judge(question: str, answer_a: str, answer_b: str, model: str = "gpt-4o") -> PairwiseVerdict:
    resp = client.beta.chat.completions.parse(
        model=model,
        temperature=0.0,
        response_format=PairwiseVerdict,
        messages=[
            {"role": "system", "content": "Compare candidate answers A and B. Pick the winner based on accuracy, groundedness, and concise formatting."},
            {"role": "user", "content": f"Question: {question}\n\nAnswer A:\n{answer_a}\n\nAnswer B:\n{answer_b}"},
        ],
    )
    return resp.choices[0].message.parsed

def pairwise_judge_debiased(question: str, ans_a: str, ans_b: str, model: str = "gpt-4o") -> dict:
    flip = random.random() < 0.5
    if flip:
        verdict = pairwise_judge(question, ans_b, ans_a, model=model)
        actual_winner = "B" if verdict.winner == "A" else "A"
    else:
        verdict = pairwise_judge(question, ans_a, ans_b, model=model)
        actual_winner = verdict.winner
    return {"winner": actual_winner, "flipped": flip, "reasoning": verdict.reasoning}