"""CLI query script for results.db."""
import sqlite3
import sys
from pathlib import Path


def show_runs(con: sqlite3.Connection) -> None:
    print(f"\n{'id':>4}  {'started':>12}  {'questions':>9}  {'retries':>7}  {'cost_usd':>9}  {'fail':>5}  {'fake':>5}")
    cursor = con.execute(
        "SELECT id, started_at, n_questions, n_retries_total, total_cost_usd, fail_rate, use_fake FROM runs ORDER BY id DESC"
    )
    for row in cursor.fetchall():
        print(f"{row[0]:>4}  {row[1]:>12.1f}  {row[2]:>9}  {row[3]:>7}  {row[4]:>9.4f}  {row[5]:>5.2f}  {row[6]:>5}")
    print()


def search_answers(con: sqlite3.Connection, pattern: str) -> None:
    cursor = con.execute(
        "SELECT id, run_id, retries, question, answer FROM answers WHERE question LIKE ? ORDER BY id",
        (f"%{pattern}%",),
    )
    rows = cursor.fetchall()
    print(f"\nFound {len(rows)} matching answers for pattern '{pattern}':\n")
    for r in rows:
        print(f"[#{r[0]} run={r[1]} retries={r[2]}] {r[3]}")
        print(f"   -> {r[4][:140]}...\n")


def main() -> None:
    if not Path("results.db").exists():
        print("Error: results.db not found. Run the pipeline first.")
        return

    with sqlite3.connect("results.db") as con:
        if len(sys.argv) > 1 and sys.argv[1] == "--runs":
            show_runs(con)
        else:
            term = sys.argv[1] if len(sys.argv) > 1 else ""
            search_answers(con, term)


if __name__ == "__main__":
    main()