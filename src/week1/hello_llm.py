"""hello_llm.py — Your first OpenAI API call.

Run it from the repo root:
    python -m src.week1.hello_llm "What is RAG in one sentence?"
"""
import sys
from openai import OpenAI
from src.config import OPENAI_BASE_URL, OPENAI_MODEL

# Connect using the Vocareum proxy base URL if configured in .env
client = OpenAI(base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else OpenAI()

def ask(question: str) -> str:
    """Send one question to the LLM and return the answer text."""
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are concise."},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Say hello in one sentence."
    print(ask(q))