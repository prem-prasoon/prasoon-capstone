"""SQLite persistence module for batch runs and answers."""
import sqlite3
import time
from pathlib import Path
from typing import Any
from src.week2.pipeline.settings import RunSummary

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at REAL,
    elapsed_seconds REAL,
    n_questions INTEGER,
    n_succeeded INTEGER,
    n_retries_total INTEGER,
    total_cost_usd REAL,
    fail_rate REAL,
    use_fake INTEGER
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER,
    question TEXT,
    answer TEXT,
    cost_usd REAL,
    retries INTEGER DEFAULT 0,
    ts REAL,
    FOREIGN KEY(run_id) REFERENCES runs(id)
);
"""


def connect(path: str | Path = "results.db") -> sqlite3.Connection:
    con = sqlite3.connect(str(path))
    con.executescript(SCHEMA)
    con.commit()
    return con


def write_run(con: sqlite3.Connection, summary: RunSummary) -> int:
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO runs (
            started_at, elapsed_seconds, n_questions, n_succeeded,
            n_retries_total, total_cost_usd, fail_rate, use_fake
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            summary.started_at,
            summary.elapsed_seconds,
            summary.n_questions,
            summary.n_succeeded,
            summary.n_retries_total,
            summary.total_cost_usd,
            summary.fail_rate,
            1 if summary.use_fake else 0,
        ),
    )
    con.commit()
    return int(cur.lastrowid)


def write_answers(con: sqlite3.Connection, run_id: int, answers: list[Any]) -> int:
    rows = [
        (run_id, a.question, a.text, a.cost_usd, a.retries, time.time())
        for a in answers
    ]
    cur = con.cursor()
    cur.executemany(
        """
        INSERT INTO answers (run_id, question, answer, cost_usd, retries, ts)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    con.commit()
    return len(rows)