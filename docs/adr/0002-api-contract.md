# ADR 0002 — Public API Contract for /v1/ask

- **Author:** Prem Prasoon
- **Date:** 2026-09-18
- **Status:** Accepted

## Context
We need a stable HTTP interface for our question-answering service that decouples external clients (such as the Streamlit UI or downstream eval suites) from the internal pipeline implementations in `src/week2/pipeline/`.

## Decision
We expose three core public endpoints via FastAPI:

1. **`GET /health`**
   - **Response:** `{"status": "ok"}` (HTTP 200)
   - Liveness and readiness probe for health monitoring.

2. **`POST /ask_batched`**
   - **Request:** `{"question": string}`
   - **Response:** `{"content": string, "cost_usd": float, "retries": int}`
   - Synchronous fallback returning a complete answer in one JSON response.

3. **`POST /ask`**
   - **Request:** `{"question": string}`
   - **Response:** Chunked plain-text stream (`media_type="text/plain"`) simulating token streaming with 50 ms intervals.

Internal translations: The public model (`Question.question`) maps to the internal pipeline (`Question.text`), and internal `Answer.text` maps back to public `Answer.content`.

## Consequences
- Internal refactoring inside `src/` will not break external clients as long as the adapter layer in `api/main.py` respects this schema.
- Self-observability metrics (`/metrics`) remain internal and are not part of the external versioned contract.