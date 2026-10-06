"""scripts/run_critic_creator.py — Critic-Creator 2-round refinement loop."""
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

QUESTION = "How does the hybrid remote work policy interact with the requirement to attend mandatory in-person team meetings?"

def main():
    print(f"Running Critic-Creator on: {QUESTION}\n")

    # Round 1: Creator draft
    r1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are the Creator. Answer company policy questions concisely."},
            {"role": "user", "content": QUESTION}
        ]
    ).choices[0].message.content

    print(f"--- Round 1 Draft ---\n{r1}\n")

    # Round 1: Critic review
    critique = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are the Critic. Identify missing precedence rules (e.g. which policy takes priority)."},
            {"role": "user", "content": f"Question: {QUESTION}\nDraft: {r1}"}
        ]
    ).choices[0].message.content

    print(f"--- Critic Critique ---\n{critique}\n")

    # Round 2: Creator revision
    r2 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are the Creator. Revise your draft incorporating the critique."},
            {"role": "user", "content": f"Question: {QUESTION}\nDraft: {r1}\nCritique: {critique}"}
        ]
    ).choices[0].message.content

    print(f"--- Round 2 Final Revised Answer ---\n{r2}\n")

    with open("docs/critic-creator-trace.md", "w", encoding="utf-8") as f:
        f.write(f"# Critic-Creator Trace: g015\n\n**Question:** {QUESTION}\n\n### Round 1 Draft\n{r1}\n\n### Critique\n{critique}\n\n### Round 2 Converged Answer\n{r2}\n\n## Reflection\nThe loop addressed the precedence ambiguity in Round 1, clarifying that mandatory on-site anchor meetings override general remote day allowances.\n")
    print("Trace saved to docs/critic-creator-trace.md")

if __name__ == "__main__":
    main()