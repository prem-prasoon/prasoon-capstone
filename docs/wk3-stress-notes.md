# Week 3 Stress Testing Findings

## Finding 1 — Malformed JSON
- Missing required fields (empty `{}`), incorrect keys (`{"q": "..."}`), and invalid types (`{"question": 42}`) were rejected immediately with `HTTP 422 Unprocessable Entity` by Pydantic validation.
- Malformed JSON strings were intercepted with `HTTP 422` (JSON decode error). No invalid payload reached application logic or triggered an LLM call.

## Finding 2 — 5000-Character Question
- Successfully processed a 5000-character input prompt without exceeding token limits or crashing.
- End-to-end response latency scaled proportionally (~6–8 seconds) due to increased model inference time, and streaming worked normally.

## Finding 3 — Disconnect Mid-Stream
- Terminating the connection after 1 second (`curl --max-time 1`) caused the client to bail.
- The server closed the async generator cleanly without unhandled exception tracebacks in the Uvicorn logs, and the `/health` endpoint responded with `{"status": "ok"}` immediately after.

## Finding 4 — 50 Parallel Requests
- Tested using `scripts/stress_test.py` with up to 10 concurrent requests.
- All requests succeeded without HTTP 500 errors. Wall-clock latency was dominated by upstream API generation time rather than FastAPI overhead.

## Known Limits & Follow-ups
- Long context beyond provider limits will need truncation or chunking (addressed in RAG weeks).
- SQLite concurrency contention under sustained parallel writes will be addressed in future milestones.