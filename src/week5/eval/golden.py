"""src/week5/eval/golden.py — Golden set loader and validator."""
from __future__ import annotations

import json
from pathlib import Path

def validate_golden_set(path: str = "data/golden_set.jsonl") -> dict:
    """Validate 20-entry distribution: 14 happy, 4 harder, 2 edge."""
    lines = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    coverage = {"happy": 0, "harder": 0, "edge": 0}
    ids = []

    for item in lines:
        ids.append(item["id"])
        notes = item.get("notes", "").lower()
        if notes.startswith("happy"):
            coverage["happy"] += 1
        elif notes.startswith("harder"):
            coverage["harder"] += 1
        elif notes.startswith("edge"):
            coverage["edge"] += 1

    return {
        "path": str(path),
        "n": len(lines),
        "ids": ids,
        "coverage": coverage,
    }