"""pipeline.py — Week 4 async pipeline supporting multiple models and Ollama."""
import asyncio
import csv
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from src.config import OPENAI_BASE_URL, OPENAI_MODEL
from src.week2.pipeline.cost import compute_cost_usd
from src.week2.pipeline.fake_llm import FakeLLMError, fake_ask_llm
from src.week2.pipeline.logging_config import get_logger
from src.week2.pipeline.settings import RunSummary, Settings

load_dotenv()
log = get_logger()


def _make_client(settings: Settings) -> AsyncOpenAI:
    """Return AsyncOpenAI configured for Ollama or hosted OpenAI/Vocareum."""
    model_name = getattr(settings, "model", "") or ""
    if model_name.startswith("llama") or model_name.startswith("ollama:"):
        return AsyncOpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # Ollama ignores the key but requires non-empty string
        )
    return AsyncOpenAI(base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else AsyncOpenAI()


class Question(BaseModel):
    text: str


class Answer(BaseModel):
    question: str
    text: str
    model: str = "default"
    confidence: float = 0.85
    sources: list[str] = Field(default_factory=lambda: ["knowledge_base"])
    cost_usd: float = 0.0
    retries: int = 0


def load_questions(path: str | Path = "data/questions.csv") -> list[Question]:
    with open(path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [Question(text=row["text"]) for row in reader if row.get("text")]


async def ask_llm(q: Question, settings: Settings | None = None) -> Answer:
    settings = settings or Settings()
    active_model = getattr(settings, "model", None) or OPENAI_MODEL

    # Route to fake LLM simulator if configured
    if settings.use_fake:
        content = await fake_ask_llm(q, fail_rate=settings.fail_rate)
        return Answer(
            question=q.text,
            text=content.text,
            model="fake",
            confidence=0.9,
            cost_usd=0.0,
            retries=0,
        )

    client = _make_client(settings)

    completion = await client.chat.completions.create(
        model=active_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a technical assistant. Provide a concise, factual answer in 2-3 sentences."
                ),
            },
            {"role": "user", "content": q.text},
        ],
        temperature=0.2,
    )

    ans_text = completion.choices[0].message.content or ""
    
    # Calculate exact cost via token usage
    usage = completion.usage
    p_tokens = usage.prompt_tokens if usage else 0
    c_tokens = usage.completion_tokens if usage else 0
    cost = compute_cost_usd(active_model, p_tokens, c_tokens)

    log.info(f"[{active_model}] asked: {q.text[:40]} | cost: ${cost:.6f}")

    return Answer(
        question=q.text,
        text=ans_text,
        model=active_model,
        confidence=0.88 if not active_model.startswith("llama") else 0.75,
        cost_usd=cost,
    )


async def ask_llm_with_retry(
    q: Question, 
    tries: int = 3, 
    settings: Settings | None = None
) -> Answer:
    for attempt in range(tries):
        try:
            ans = await ask_llm(q, settings=settings)
            ans.retries = attempt
            return ans
        except (FakeLLMError, ConnectionError, Exception) as exc:
            if attempt == tries - 1:
                log.error(f"Failed after {tries} attempts: {q.text[:40]} ({exc})")
                raise
            log.warning(f"retry {attempt + 1} for: {q.text[:40]} ({exc})")
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


async def run_in_batches(
    questions: list[Question], 
    batch_size: int = 5,
    settings: Settings | None = None,
) -> list[Answer]:
    out: list[Answer] = []
    for i in range(0, len(questions), batch_size):
        chunk = questions[i : i + batch_size]
        log.info(f"batch {i // batch_size + 1}: {len(chunk)} questions")
        batch_answers = await asyncio.gather(
            *(ask_llm_with_retry(q, settings=settings) for q in chunk)
        )
        out.extend(batch_answers)
        await asyncio.sleep(0.1)
    return out


def summarise_run(
    answers: list[Answer],
    *,
    started_at: float,
    elapsed: float,
    fail_rate: float,
    use_fake: bool,
) -> RunSummary:
    return RunSummary(
        started_at=started_at,
        elapsed_seconds=round(elapsed, 2),
        n_questions=len(answers),
        n_succeeded=len(answers),
        n_retries_total=sum(a.retries for a in answers),
        total_cost_usd=round(sum(a.cost_usd for a in answers), 6),
        fail_rate=fail_rate,
        use_fake=use_fake,
    )


if __name__ == "__main__":
    from src.week2.pipeline.store import connect, write_answers, write_run

    settings = Settings()
    log.info(f"config: {settings.model_dump(mode='json')}")

    questions = load_questions(settings.questions_csv)
    log.info(f"loaded {len(questions)} questions")

    started = time.time()
    answers = asyncio.run(
        run_in_batches(questions, batch_size=settings.batch_size, settings=settings)
    )
    elapsed = time.time() - started

    summary = summarise_run(
        answers,
        started_at=started,
        elapsed=elapsed,
        fail_rate=settings.fail_rate,
        use_fake=settings.use_fake,
    )
    log.info(f"summary: {summary.model_dump_json()}")

    # 1. Export JSON
    payload = {
        "summary": summary.model_dump(mode="json"),
        "answers": [a.model_dump() for a in answers],
    }
    settings.results_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwrote {len(answers)} answers to {settings.results_json} in {elapsed:.2f}s\n")

    # 2. Persist to SQLite
    with connect(settings.results_db) as con:
        run_id = write_run(con, summary)
        n = write_answers(con, run_id, answers)
        log.info(f"persisted run {run_id} with {n} answers to {settings.results_db}")