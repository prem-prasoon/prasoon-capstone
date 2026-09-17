# W4 Activity — Ollama Three-Way Model Comparison

## Setup
- **Hosted Models:** `gpt-4o-mini`, `gpt-4o` (via OpenAI / Vocareum proxy).
- **Local Model:** `llama3.2:3b` running via Ollama (`http://localhost:11434/v1`).
- **Cost Registry:** `cost.py` maps tokens to pricing rates, treating local models as `$0.00` marginal cost.

## Results Summary
| Model | Questions (n) | Total Cost (USD) | Avg Cost / Query | Avg Confidence |
|---|---|---|---|---|
| **gpt-4o** | 10 | ~$0.013648 | ~$0.001365 | 0.91 |
| **gpt-4o-mini** | 10 | ~$0.000832 | ~$0.000083 | 0.87 |
| **llama3.2:3b** | 10 | **$0.000000** | **$0.000000** | 0.75 |

## Observations & Quality Gap
1. **Cost Ratio:** Hosted models charge per token, whereas local execution has an infinite cost-reduction ratio ($0 marginal cost after hardware setup).
2. **Definitional vs Synthesis:** `llama3.2:3b` handles simple definitional queries well (e.g., "What is RAG?"), but omits operational nuances (safety, migrations, multi-environment synchronization) on synthesis questions like schema versioning.
3. **Calibrated Confidence:** Average reported confidence drops predictably as model size scales down (0.91 -> 0.87 -> 0.75), indicating the 3B model is self-aware of its uncertainty.
4. **Primary Use Cases for Local:** Rapid prompt engineering iteration without token costs, and privacy-critical environments where data cannot leave the perimeter.