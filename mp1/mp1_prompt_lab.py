"""mp1/mp1_prompt_lab.py — Execution, scoring, and benchmarking harness.

Conforms to MP1 Starter Template and FAQ rubrics without requiring the
optional 'tabulate' package.
"""

import asyncio
import json
import os
from pathlib import Path
import re
import sys
import time
from dotenv import load_dotenv
from openai import AsyncOpenAI
import pandas as pd

# ************************************************************
#                      Environment & Setup
# ************************************************************

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(CURRENT_DIR / ".env")

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(CURRENT_DIR))

try:
  from src.config import OPENAI_BASE_URL
except ImportError:
  OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)

from prompts import (
    COT_PROMPT,
    FEW_SHOT_PROMPT,
    STRUCTURED_ROLE_PROMPT,
    ZERO_SHOT_PROMPT,
)

client = AsyncOpenAI(base_url=OPENAI_BASE_URL) if OPENAI_BASE_URL else AsyncOpenAI()

MODEL = "gpt-4o-mini"
JUDGE_MODEL = "gpt-4o"
TEMPERATURE = 0.0

STRATEGIES = {
    "zero_shot": ZERO_SHOT_PROMPT,
    "few_shot": FEW_SHOT_PROMPT,
    "structured": STRUCTURED_ROLE_PROMPT,
    "cot": COT_PROMPT,
}

RATES = {
    "gpt-4o-mini": {"in": 0.15 / 1_000_000, "out": 0.60 / 1_000_000},
    "gpt-4o": {"in": 2.50 / 1_000_000, "out": 10.00 / 1_000_000},
}


# ************************************************************
#                     Response Parsing Helpers
# ************************************************************


def parse_response(raw: str) -> dict | None:
  """Extract and parse JSON object from markdown code fences or plain text."""
  if not raw or not isinstance(raw, str):
    return None
  raw = raw.strip()

  # 1. Match ```json ... ``` blocks
  match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
  if match:
    block = match.group(1).strip()
    first_b = block.find("{")
    last_b = block.rfind("}")
    if first_b != -1 and last_b != -1 and last_b > first_b:
      try:
        data = json.loads(block[first_b : last_b + 1])
        return data if isinstance(data, dict) else None
      except Exception:
        pass

  # 2. Match outermost balanced braces
  first_brace = raw.find("{")
  last_brace = raw.rfind("}")
  if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
    try:
      data = json.loads(raw[first_brace : last_brace + 1].strip())
      return data if isinstance(data, dict) else None
    except Exception:
      pass

  # 3. Direct JSON load fallback
  try:
    data = json.loads(raw)
    return data if isinstance(data, dict) else None
  except Exception:
    return None


# ************************************************************
#                     Async Execution
# ************************************************************


async def run_one(strategy_name: str, snippet: dict) -> dict:
  """Run one strategy on one snippet, returning all captured fields."""
  prompt_template = STRATEGIES[strategy_name]
  prompt_text = snippet.get("snippet") or snippet.get("text", "")
  full_prompt = prompt_template.format(snippet=prompt_text)

  start = time.time()
  try:
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": full_prompt}],
        temperature=TEMPERATURE,
    )
    duration = time.time() - start
    raw_text = resp.choices[0].message.content or ""
    tokens = resp.usage
    cost = (
        (tokens.prompt_tokens * RATES[MODEL]["in"])
        + (tokens.completion_tokens * RATES[MODEL]["out"])
        if tokens
        else 0.0
    )
  except Exception:
    duration = time.time() - start
    raw_text = ""
    cost = 0.0

  parsed = parse_response(raw_text)
  return {
      "strategy": strategy_name,
      "snippet_id": snippet["id"],
      "snippet_text": prompt_text,
      "raw_response": raw_text,
      "parsed": parsed,
      "parse_success": parsed is not None,
      "cost_usd": cost,
      "latency_s": duration,
  }


async def run_all(snippets: list[dict]) -> list[dict]:
  """Execute all 10 snippets x 4 strategies = 40 parallel calls."""
  tasks = [run_one(s_name, snip) for s_name in STRATEGIES for snip in snippets]
  return await asyncio.gather(*tasks)


# ************************************************************
#                      Scoring & LLM Judge (1-4 Rubric)
# ************************************************************


def normalize_experience(val: any) -> int | None:
  """Normalize experience variants (e.g. '5+', 'around 6', '3-5' min) into integers."""
  if val is None or val == "null":
    return None
  if isinstance(val, (int, float)):
    return int(val)
  val_str = str(val).lower().strip()
  if val_str in ["none", "null", "not required", "freshers"]:
    return None
  if "fresh" in val_str or "entry" in val_str:
    return 0
  match = re.search(r"\d+", val_str)
  return int(match.group(0)) if match else None


def score_accuracy(extracted: dict | None, gold: dict) -> int:
  """Compare 3 fields case-insensitively and return score (0, 1, 2, or 3)."""
  if not extracted or not isinstance(extracted, dict):
    return 0
  score = 0

  c_pred = str(extracted.get("company", "")).strip().lower()
  c_gold = str(gold.get("company", "")).strip().lower()
  if c_pred and (c_pred in c_gold or c_gold in c_pred):
    score += 1

  r_pred = str(extracted.get("role", "")).strip().lower()
  r_gold = str(gold.get("role", "")).strip().lower()
  if r_pred and (r_pred in r_gold or r_gold in r_pred):
    score += 1

  e_pred = normalize_experience(extracted.get("years_experience_required"))
  e_gold = gold.get("years_experience_required")
  if e_pred == e_gold:
    score += 1
  elif e_pred in [0, None] and e_gold in [0, None]:
    score += 1

  return score


async def score_llm_judge(
    snippet_text: str, extracted: dict | None, gold: dict
) -> int:
  """Prompt gpt-4o judge using the 1-4 scale from the course rubric."""
  if not extracted:
    return 1

  judge_prompt = f"""You are evaluating an LLM extraction against ground truth.

Job Snippet: "{snippet_text}"
Ground Truth: {json.dumps(gold)}
Extracted Data: {json.dumps(extracted)}

Rubric:
4 — all three fields correct
3 — two of three correct, no fabricated data
2 — one of three correct, or fabricated a field
1 — none correct or unparsable

Output ONLY valid JSON with keys "score" (integer 1-4) and "reasoning" (one short sentence):
{{"score": <1-4>, "reasoning": "<explanation>"}}"""

  try:
    res = await client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=TEMPERATURE,
    )
    parsed_judge = parse_response(res.choices[0].message.content or "")
    if parsed_judge and "score" in parsed_judge:
      return int(parsed_judge["score"])
    return 3
  except Exception:
    return 3


# ************************************************************
#                      Main Runner & Table Output
# ************************************************************


async def main():
  print("--- Starting MP1 Evaluation Pipeline ---")
  data_dir = CURRENT_DIR / "data"
  snippets_path = data_dir / "job_snippets.jsonl"
  golden_path = data_dir / "golden_set.jsonl"

  if not snippets_path.exists() or not golden_path.exists():
    print("ERROR: Missing data files in mp1/data/")
    return

  snippets = [
      json.loads(line)
      for line in snippets_path.read_text(encoding="utf-8").splitlines()
      if line.strip()
  ]
  golden_map = {
      item["id"]: item
      for item in [
          json.loads(line)
          for line in golden_path.read_text(encoding="utf-8").splitlines()
          if line.strip()
      ]
  }

  print(f"Loaded {len(snippets)} snippets. Executing 40 parallel calls...")
  results = await run_all(snippets)

  print(f"Running LLM-as-a-Judge evaluations with {JUDGE_MODEL}...")
  judge_tasks = [
      score_llm_judge(
          r["snippet_text"], r["parsed"], golden_map[r["snippet_id"]]
      )
      for r in results
  ]
  judge_scores = await asyncio.gather(*judge_tasks)

  scored = []
  for r, j_score in zip(results, judge_scores):
    gold = golden_map[r["snippet_id"]]
    acc = score_accuracy(r["parsed"], gold)
    scored.append({
        "strategy": r["strategy"],
        "snippet_id": r["snippet_id"],
        "accuracy": acc,
        "parse_success": r["parse_success"],
        "llm_judge_score": j_score,
        "cost_usd": r["cost_usd"],
        "latency_s": r["latency_s"],
    })

  # Step 5 Aggregation using Pandas
  df = pd.DataFrame(scored)

  summary = df.groupby("strategy").agg({
      "accuracy": "mean",
      "parse_success": "mean",
      "llm_judge_score": "mean",
      "cost_usd": "sum",
      "latency_s": "median",
  })
  summary.columns = [
      "Accuracy (mean of 3)",
      "Parse rate",
      "Judge score",
      "Total cost ($)",
      "Latency p50 (s)",
  ]

  print("\n--- Summary Table ---")
  print(summary.round(3))

  # Build Markdown comparison report without relying on tabulate
  comparison_md = "# MP1 Strategy Evaluation Comparison\n\n"
  comparison_md += "## Summary by Strategy\n\n"
  comparison_md += (
      "| Strategy | Accuracy (mean of 3) | Parse Rate | Judge Score (1-4) |"
      " Total Cost ($) | Latency p50 (s) |\n| :--- | :---: | :---: | :---: |"
      " :---: | :---: |\n"
  )
  for s_name, row in summary.iterrows():
    comparison_md += (
        f"| **{s_name}** | {row['Accuracy (mean of 3)']:.2f} / 3 | "
        f"{row['Parse rate'] * 100:.0f}% | {row['Judge score']:.2f} / 4 | "
        f"${row['Total cost ($)']:.6f} | {row['Latency p50 (s)']:.2f}s |\n"
    )

  comparison_md += "\n## Detailed Per-Snippet Execution Log (40 Runs)\n\n"
  comparison_md += (
      "| # | Strategy | Snippet ID | Accuracy (/ 3) | Parse Success | Judge"
      " Score (1-4) | Cost ($) | Latency (s) |\n| :--- | :--- | :---: | :---: |"
      " :---: | :---: | :---: | :---: |\n"
  )
  for idx, r in enumerate(scored):
    comparison_md += (
        f"| {idx} | {r['strategy']} | {r['snippet_id']} | {r['accuracy']} | "
        f"{r['parse_success']} | {r['llm_judge_score']} | ${r['cost_usd']:.6f}"
        f" | {r['latency_s']:.2f}s |\n"
    )

  output_file = CURRENT_DIR / "mp1_comparison.md"
  output_file.write_text(comparison_md, encoding="utf-8")
  print(f"\nSaved comparison results to {output_file.name}")


if __name__ == "__main__":
  asyncio.run(main())