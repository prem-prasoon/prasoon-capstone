import sys
from openai import OpenAI
from src.config import OPENAI_BASE_URL, OPENAI_MODEL

client = OpenAI(base_url=OPENAI_BASE_URL)

def ask_llm(prompt: str) -> str:
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return completion.choices[0].message.content

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "Explain retrieval-augmented generation in three sentences."
    answer = ask_llm(prompt)
    print(answer)
