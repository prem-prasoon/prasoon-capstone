"""src/week5/pipeline/store.py — SQLite storage for answers and evaluation runs."""
import sqlite3
from pathlib import Path

def ensure_schema(db_path: str = "data/answers.db"):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eval_runs (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            golden_id         TEXT NOT NULL,
            question          TEXT NOT NULL,
            candidate_answer  TEXT NOT NULL,
            ideal_answer      TEXT NOT NULL,
            candidate_model   TEXT NOT NULL,
            judge_model       TEXT NOT NULL,
            accuracy          INTEGER NOT NULL,
            groundedness      INTEGER NOT NULL,
            format            INTEGER NOT NULL,
            reasoning         TEXT NOT NULL,
            eval_run_label    TEXT DEFAULT 'eval-run-001',
            created_at        TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_schema()
    print("Schema verified: eval_runs table ready in data/answers.db")