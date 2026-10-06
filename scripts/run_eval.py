"""scripts/run_eval.py — Run evaluation against the golden set and persist to SQLite."""
import argparse
import asyncio
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from src.week5.eval.judge import judge_one
from src.week5.pipeline.store import ensure_schema

async def get_candidate_answer(client: httpx.AsyncClient, api_url: str, question: str) -> str:
    res = await client.post(
        f"{api_url}/ask",
        json={"question": question},
        timeout=httpx.Timeout(120.0, connect=10.0),
    )
    res.raise_for_status()
    return res.json().get("content", "")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden-set", default="data/golden_set.jsonl")
    parser.add_argument("--db", default="data/answers.db")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--judge-model", default="gpt-4o")
    parser.add_argument("--label", default="eval-run-001")
    args = parser.parse_args()

    ensure_schema(args.db)

    with open(args.golden_set, "r", encoding="utf-8") as f:
        golden_entries = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(golden_entries)} entries. Running evaluation...")
    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    async with httpx.AsyncClient() as http_client:
        for entry in golden_entries:
            gid = entry["id"]
            q = entry["question"]
            ideal = entry["ideal_answer"]
            
            print(f"Evaluating {gid}: {q[:50]}...")
            try:
                candidate = await get_candidate_answer(http_client, args.api_url, q)
                score = judge_one(q, candidate, ideal, model=args.judge_model)

                cur.execute("""
                    INSERT INTO eval_runs (
                        golden_id, question, candidate_answer, ideal_answer,
                        candidate_model, judge_model, accuracy, groundedness, format,
                        reasoning, eval_run_label
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    gid, q, candidate, ideal, "gpt-4o-mini", args.judge_model,
                    score.accuracy, score.groundedness, score.format,
                    score.reasoning, args.label
                ))
                conn.commit()
                print(f"  -> {gid} scored: acc={score.accuracy}, ground={score.groundedness}, fmt={score.format}")
            except Exception as e:
                print(f"  -> Error on {gid}: {e}")

    conn.close()
    print(f"\nEvaluation complete. Persisted rows under label '{args.label}'.")

if __name__ == "__main__":
    asyncio.run(main())