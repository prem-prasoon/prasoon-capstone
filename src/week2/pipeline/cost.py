"""cost.py — Token-based pricing and cost calculation across models."""

# Rates per token (prompt_rate, completion_rate)
RATES: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15 / 1_000_000, 0.60 / 1_000_000),
    "gpt-4o": (2.50 / 1_000_000, 10.00 / 1_000_000),
    "llama3.2:3b": (0.0, 0.0),  # Local Ollama model ($0 marginal cost)
}


def compute_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate USD cost based on token counts and model pricing."""
    if model.startswith("llama") or model.startswith("ollama:"):
        return 0.0

    prompt_rate, completion_rate = RATES.get(model, (0.0, 0.0))
    total_cost = (prompt_tokens * prompt_rate) + (completion_tokens * completion_rate)
    return round(total_cost, 6)