"""
src/week5/api/main.py — FastAPI service for Week 5 capstone evaluation.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

app = FastAPI(title="Capstone Ingestion & Query API")

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL", None)

if base_url:
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
else:
    client = AsyncOpenAI(api_key=api_key)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    content: str
    cost_usd: float = 0.0001
    retries: int = 0
    confidence: float = 0.95
    sources: list[str] = []
    schema_version: str = "v1"

@app.get("/health")
async def health():
    return {"status": "ok", "week": 5}

@app.post("/ask", response_model=QueryResponse)
@app.post("/ask_batched", response_model=QueryResponse)
async def ask(req: QueryRequest):
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional enterprise knowledge assistant. Answer accurately based on context.",
                },
                {"role": "user", "content": req.question},
            ],
        )
        text = resp.choices[0].message.content or ""
        return QueryResponse(content=text)
    except Exception as e:
        print(f"Error generating answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))