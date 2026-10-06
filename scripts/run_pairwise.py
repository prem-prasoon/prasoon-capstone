"""scripts/run_pairwise.py — A/B comparison between two system prompts with debiasing."""
import asyncio
import json
import random
import httpx
from openai import OpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

PROMPT_V1 = "You are an Enterprise Knowledge Assistant. Answer accurately based on context."
PROMPT_V2 = "You are an Enterprise Knowledge Assistant. Answer accurately, cite relevant policy guidelines, and state clearly if information is not found."

class PairwiseVerdict(BaseModel):
    winner: str = Field(pattern="^[AB]$")
    reasoning: str

def pairwise_judge(q: str, ans_a: str, ans_b: str) -> PairwiseVerdict:
    resp = client.beta.chat.completions.parse(
        model="gpt-4o",
        temperature=0.0,
        response_format=PairwiseVerdict,
        messages=[
            {"role": "system", "content": "Compare Answer A and Answer B. Pick the winner based on accuracy, groundedness, and formatting clarity."},
            {"role": "user", "content": f"Question: {q}\n\nAnswer A:\n{ans_a}\n\nAnswer B:\n{ans_b}"}
        ]
    )
    return resp.choices[0].message.parsed

async def generate(prompt: str, q: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": q}]
    )
    return resp.choices[0].message.content or ""

async def main():
    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()][:5]

    v1_wins, v2_wins = 0, 0
    print("Running Pairwise Evaluation on 5 samples...")
    for item in entries:
        q = item["question"]
        ans1 = await generate(PROMPT_V1, q)
        ans2 = await generate(PROMPT_V2, q)

        flip = random.random() < 0.5
        if flip:
            verdict = pairwise_judge(q, ans2, ans1)
            actual_winner = "v2" if verdict.winner == "A" else "v1"
        else:
            verdict = pairwise_judge(q, ans1, ans2)
            actual_winner = "v1" if verdict.winner == "A" else "v2"

        if actual_winner == "v1":
            v1_wins += 1
        else:
            v2_wins += 1
        print(f"  {item['id']}: Winner -> {actual_winner}")

    print(f"\nResults: v1 wins = {v1_wins} | v2 wins = {v2_wins}")

if __name__ == "__main__":
    asyncio.run(main())