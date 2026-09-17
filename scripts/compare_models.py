import sys
from pathlib import Path

# Add project root to sys.path so 'src' can be imported cleanly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import argparse
import asyncio
import sqlite3
import time
from src.week2.pipeline.pipeline import Question, ask_llm_with_retry, load_questions
from src.week2.pipeline.settings import Settings


def init_db(db_path: str = "data/answers.db"):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT,
            question TEXT,
            content TEXT,
            confidence REAL,
            cost_usd REAL,
            retries INTEGER,
            created_at REAL
        )
        """
    )
    con.commit()
    con.close()


def store_answer(ans, db_path: str = "data/answers.db"):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO answers (model, question, content, confidence, cost_usd, retries, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ans.model,
            ans.question,
            ans.text,
            ans.confidence,
            ans.cost_usd,
            ans.retries,
            time.time(),
        ),
    )
    con.commit()
    con.close()


async def run_comparison(models: list[str]):
    init_db()
    questions = load_questions("data/questions.csv")

    for model_name in models:
        print(f"\n================ Running model: {model_name} ================")
        settings = Settings(model=model_name, use_fake=False)
        total_cost = 0.0

        for q in questions:
            ans = await ask_llm_with_retry(q, settings=settings)
            store_answer(ans)
            total_cost += ans.cost_usd
            print(f"  [{model_name}] Q: {q.text[:35]}... -> Cost: ${ans.cost_usd:.6f}")

        print(f"Done {model_name}. Total Cost: ${total_cost:.6f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        default="gpt-4o-mini",
        help="Comma-separated model names (e.g., gpt-4o-mini,llama3.2:3b)",
    )
    args = parser.parse_args()
    model_list = [m.strip() for m in args.models.split(",")]
    asyncio.run(run_comparison(model_list))