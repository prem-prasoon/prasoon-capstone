# 0002. Prompt Strategy for Entity Extraction and Ingestion

**Status:** Accepted  
**Date:** 2026-09-20  
**Context:** MP1 Prompt Lab / Phase 1 Foundations  

## Context and Problem Statement
Our backend ingestion pipeline requires extracting structured metadata (company, role, years of experience) from unstructured text inputs. Downstream services require strictly formatted payloads that conform to schema definitions without runtime deserialization exceptions.

We evaluated four candidate prompting strategies in `mp1/`:
1. Zero-shot
2. Few-shot
3. Structured / Role-based
4. Chain-of-thought (CoT)

## Decision
We choose **Structured / Role-based Prompting** as the primary ingestion strategy for the capstone pipeline.

## Evaluation Summary
Based on benchmark runs across 40 test executions (`mp1_comparison.md`):
- **Structured Prompting** achieved 3.00 / 3 accuracy, a 100% JSON parse rate, and a 3.90 / 4 judge score with low latency (~1.86s p50) and low cost ($0.000436 total).
- **Zero-shot** had lower cost ($0.000340) but scored lower on the judge rubric (3.50 / 4) due to less consistent output formatting.
- **Few-shot** scored 2.90 / 3 accuracy and 3.70 / 4 judge score, but added persistent token overhead across every call ($0.000403).
- **Chain-of-thought** produced accurate results (3.00 / 3, 3.80 / 4), but generated reasoning tokens that increased median latency to 2.24s and increased costs to $0.000652 (roughly 50% higher).

## Consequences
### Positive
- Reliable JSON structure that serializes directly into Pydantic models.
- Low latency suitable for synchronous API requests.
- Cost-efficient token utilization compared to Few-shot and Chain-of-thought.

### Negative / Trade-offs
- Highly ambiguous or domain-novel text may require occasional exemplar injection. If schema adherence degrades in later phases, targeted few-shot examples will be appended dynamically.