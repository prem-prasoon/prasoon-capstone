"""api/main.py — FastAPI service exposing streaming and batch LLM endpoints."""
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.week2.pipeline.pipeline import (
    Answer as _PipelineAnswer,
    Question as _PipelineQuestion,
    ask_llm as _pipeline_ask_llm,
)

app = FastAPI(
    title="Capstone API",
    description="Asynchronous Question-Answering Service with Streaming and Batch LLM Interfaces.",
    version="1.0.0",
)

# ─── Observability Middleware (Week 3 Activity) ──────────────────────────────
request_counts: dict[str, int] = {}


@app.middleware("http")
async def count_requests(request, call_next):
    path = request.url.path
    request_counts[path] = request_counts.get(path, 0) + 1
    response = await call_next(request)
    return response


# ─── Public API Contract (ADR 0002) ──────────────────────────────────────────
class Question(BaseModel):
    question: str


class Answer(BaseModel):
    content: str
    cost_usd: float
    retries: int


# ─── Endpoints ───────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return {
        "endpoints": request_counts,
        "total": sum(request_counts.values()),
    }


@app.post("/ask_batched", response_model=Answer)
async def ask_batched(q: Question):
    pipeline_q = _PipelineQuestion(text=q.question)
    pipeline_ans = await _pipeline_ask_llm(pipeline_q)
    return Answer(
        content=pipeline_ans.text,
        cost_usd=pipeline_ans.cost_usd,
        retries=pipeline_ans.retries,
    )


async def stream_answer(question: str):
    pipeline_q = _PipelineQuestion(text=question)
    pipeline_ans = await _pipeline_ask_llm(pipeline_q)
    for word in pipeline_ans.text.split(" "):
        await asyncio.sleep(0.05)
        yield word + " "


@app.post("/ask")
async def ask(q: Question):
    return StreamingResponse(stream_answer(q.question), media_type="text/plain")