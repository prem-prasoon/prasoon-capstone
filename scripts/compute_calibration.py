"""scripts/compute_calibration.py — Agreement computation helper."""
from __future__ import annotations
import argparse
import re
import sqlite3
from pathlib import Path

TABLE_ROW = re.compile(r"^\|\s*(g\d+)\s*\|\s*(\d)\s*\|\s*(\d)\s*\|\s*(\d)\s*\|")

def parse_calibration_file(path: str) -> dict[str, dict[str, int]]:
    scores = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = TABLE_ROW.match(line)
        if match:
            gid, a, g, f = match.groups()
            scores[gid] = {"accuracy": int(a), "groundedness": int(g), "format": int(f)}
    return scores

def fetch_judge_scores(db_path: str, label: str, golden_ids: list[str]) -> dict[str, dict[str, int]]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    placeholders = ",".join("?" * len(golden_ids))
    cur.execute(f"""
        SELECT golden_id, accuracy, groundedness, format
        FROM eval_runs
        WHERE eval_run_label = ?
          AND golden_id IN ({placeholders})
    """, (label, *golden_ids))
    out = {gid: {"accuracy": a, "groundedness": g, "format": f} for gid, a, g, f in cur.fetchall()}
    conn.close()
    return out

def compute_agreement(mine: dict, judge: dict) -> dict:
    dimensions = ["accuracy", "groundedness", "format"]
    exact = within_1 = total = 0
    per_dim_exact = {d: 0 for d in dimensions}
    per_dim_total = {d: 0 for d in dimensions}
    disagreements = []

    for gid, my_scores in mine.items():
        if gid not in judge:
            continue
        for dim in dimensions:
            m = my_scores[dim]
            j = judge[gid][dim]
            total += 1
            per_dim_total[dim] += 1
            delta = abs(m - j)
            if delta == 0:
                exact += 1
                within_1 += 1
                per_dim_exact[dim] += 1
            elif delta == 1:
                within_1 += 1
            else:
                disagreements.append({"gid": gid, "dimension": dim, "mine": m, "judge": j, "delta": delta})

    return {
        "exact": exact, "within_1": within_1, "total": total,
        "per_dim_exact": per_dim_exact, "per_dim_total": per_dim_total,
        "disagreements": disagreements
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibration-file", default="docs/judge-calibration.md")
    parser.add_argument("--db", default="data/answers.db")
    parser.add_argument("--label", default="eval-run-001")
    args = parser.parse_args()

    mine = parse_calibration_file(args.calibration_file)
    judge = fetch_judge_scores(args.db, args.label, list(mine.keys()))
    res = compute_agreement(mine, judge)

    total = res["total"]
    print(f"\nCalibration Summary for label='{args.label}'")
    print("-" * 35)
    print(f"Entries scored         : {total // 3}")
    print(f"Dimension scores       : {total}")
    if total:
        print(f"Exact agreement        : {res['exact']}/{total} ({100*res['exact']/total:.1f}%)")
        print(f"Within-1 agreement     : {res['within_1']}/{total} ({100*res['within_1']/total:.1f}%)")
    for d, count in res["per_dim_exact"].items():
        print(f"  {d:<12} exact  : {count}/{res['per_dim_total'][d]}")
    print(f"Disagreements > 1      : {len(res['disagreements'])}")
    for item in res["disagreements"]:
        print(f"  {item['gid']} [{item['dimension']}]: Mine={item['mine']} vs Judge={item['judge']} (Delta={item['delta']})")

if __name__ == "__main__":
    main()