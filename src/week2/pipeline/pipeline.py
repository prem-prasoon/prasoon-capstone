"""pipeline.py — Demonstrates asyncio.as_completed vs asyncio.gather."""
import asyncio
import sys
from src.week2.pipeline.fake_llm import Question, Answer, fake_ask_llm


async def ask_llm_with_retry(
    q: Question,
    fail_rate: float = 0.0,
    max_retries: int = 3
) -> Answer:
    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            return await fake_ask_llm(q, fail_rate=fail_rate)
        except ConnectionError as e:
            if attempt == max_retries:
                return Answer(question=q.text, text=f"[FAILED] after {max_retries} attempts")
            print(f"  ⚠ Retry {attempt}/{max_retries} for: '{q.text[:25]}...' (backing off {backoff}s)")
            await asyncio.sleep(backoff)
            backoff *= 2.0


async def run_batch_stream(questions: list[Question], fail_rate: float = 0.0) -> list[Answer]:
    tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]
    results: list[Answer] = []
    
    # as_completed yields tasks in the order they finish (fastest first)
    for coro in asyncio.as_completed(tasks):
        ans = await coro
        print(f"  ✓ {ans.text[:60]}...")
        results.append(ans)
        
    return results


if __name__ == "__main__":
    fail_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    sample = [
        Question(text="What is RAG in one sentence?"),
        Question(text="Name three uses of vector databases."),
        Question(text="Why might an LLM hallucinate?"),
        Question(text="Explain async and await in plain language."),
        Question(text="What is the difference between a chatbot and an agent?"),
    ]

    print(f"\n--- Running run_batch_stream (fail_rate={fail_rate}) ---")
    answers = asyncio.run(run_batch_stream(sample, fail_rate=fail_rate))
    print(f"\nFinished: returned {len(answers)} answers.\n")