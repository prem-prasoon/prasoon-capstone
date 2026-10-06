# 0002. API Contract & 6-Field Answer Schema

**Status:** Locked (M1)  
**Date:** 2026-10-06  
**Context:** Week 5 / Milestone 1  

## Context
Downstream evaluation harnesses, cost accounting dashboards, and UI clients require a stable, invariant data contract before retrieval pipelines (RAG) are introduced in Week 6. Changing response schemas late causes cascading regressions across persistence and evaluation modules.

## Decision
The `/ask` and `/ask_batched` endpoints strictly return a JSON object compliant with the 6-field `Answer` schema:

```python
class Answer(BaseModel):
    content: str
    cost_usd: float
    retries: int
    confidence: float
    sources: list[str]
    schema_version: str = "v1"