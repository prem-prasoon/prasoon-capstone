"""fake_llm.py — Simulates LLM calls with latency and controlled failure rates."""
import asyncio
import random
from dataclasses import dataclass

class FakeLLMError(Exception):
    """Raised when fake_ask_llm encounters a simulated failure."""
    pass

@dataclass
class Question:
    text: str


@dataclass
class Answer:
    question: str
    text: str


async def fake_ask_llm(q: Question, fail_rate: float = 0.0) -> Answer:
    # Simulate variable API response time (0.3s to 1.5s)
    delay = random.uniform(0.3, 1.5)
    await asyncio.sleep(delay)

    # Simulate transient network / 429 rate limit errors
    if random.random() < fail_rate:
        raise ConnectionError(f"Transient API failure while processing: {q.text}")

    return Answer(
        question=q.text,
        text=f"Response to '{q.text}' (took {delay:.2f}s)"
    )