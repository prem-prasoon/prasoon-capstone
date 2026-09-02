# ADR-0001: Capstone Framing — FastAPI Knowledge Assistant

- **Status:** Draft v1
- **Date:** 2026-09-02
- **Author:** Prem Prasoon

## Context

Developers regularly spend unnecessary time navigating complex web documentation to resolve syntax and implementation queries for backend frameworks. This capstone project builds a specialized knowledge assistant targeting FastAPI reference material, enabling developers to obtain fast, grounded responses without context switching.

## Decision — Solution Framing Canvas

| Box | Your answer |
|-----|-------------|
| **Inputs** | Plain-text technical queries regarding FastAPI concepts, route creation, and deployment practices. |
| **Outputs** | Concise markdown explanations with verified code snippets and citations pointing directly to documentation sections. |
| **Tools** | OpenAI gpt-4o-mini completion API and local file system readers for initial text ingest. |
| **Memory** | Stateless execution for v1; will retain the last N conversational turns in future iterations. |
| **Autonomy level** | Retrieval-Augmented Generation assistant; operates strictly within provided context and tools without discretionary execution. |
| **Decision boundaries** | Allowed to summarize concepts and suggest syntax; production deployment and database modifications remain strictly manual. |

## Consequences

- **Positive:** Standardizes technical lookup and accelerates initial project scaffolding.
- **Positive:** Grounding queries against static documentation substantially eliminates hallucinations.
- **Negative / risks:** Latency dependency on the external OpenAI API endpoints.
- **Negative / risks:** Document chunking boundaries might occasionally break multi-part code examples.
- **Things we'll re-visit:** Document parsing strategies, embedding models, and vector database selection in subsequent ADRs.
