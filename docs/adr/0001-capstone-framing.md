# 0001. Capstone System Framing (Locked at M1)

**Status:** Locked (M1)  
**Date:** 2026-10-06  

## 1. Context
Internal employees at mid-sized knowledge enterprises spend an estimated 15–30 minutes navigating scattered intranet drives and HR portals to resolve straightforward policy questions. HR generalists and team leads are overwhelmed with redundant questions, while new hires experience delayed onboarding. 

## 2. Decision (EKA Scope)
We are building an **Enterprise Knowledge Assistant (EKA)** strictly scoped to internal company policies (HR benefits, leave rules, IT security/BYOD, and travel/expense guidelines).
- **What it does:** Ingests internal policy documents, provides direct conversational answers to employee questions, cites specific source documents, and provides structured schema outputs.
- **What it does NOT do:** It does not query public internet search, does not generate code, does not modify database records, and does not execute financial transactions or approve leave requests.
- **Tech Stack:** FastAPI, SQLite (`data/answers.db`), OpenAI models (`gpt-4o-mini` candidate generator, `gpt-4o` evaluator/judge), Python 3.12.

## 3. Stakeholders
- **Primary Consumers:** Employees (e.g., Ananya, new engineer) needing immediate, private answers to company policies.
- **Approvers:** Engineering Managers (e.g., Vikram) verifying policy caps before sign-off.
- **Domain Owners:** HR Generalists (e.g., Priya) whose manual triage workload is reduced.

## 4. Sponsor KPI Targets & Rationales
1. **Answer Accuracy & Groundedness (\(\ge 85\%\) / score \(\ge 3.4/4.0\)):**
   - *Rationale:* HR advice directly affects employee compliance and compensation. The system must achieve at least parity with human HR tier-1 triage to avoid liability and incorrect claims.
2. **Citation Precision (\(\ge 90\%\) verified sources cited):**
   - *Rationale:* Answers must provide audit-grade trust. Employees and managers will only trust automated answers if they can immediately verify the source handbook clause.
3. **P95 Latency (\(< 3.0\) seconds):**
   - *Rationale:* HR generalists and managers need answers mid-conversation with candidates or during routine approvals; delays above 3 seconds cause workflow abandonment.

## 5. Alternatives Considered & Rejected
1. **Open-Domain Agentic Search:**
   - *Rejected:* Pulling public search results violates Filter 1 (Enterprise Knowledge boundary) and risks hallucinating external regional labor laws that contradict internal policy.
2. **Deterministic FAQ Rule Engine / Elastic Keyword Match:**
   - *Rejected:* Fails on cross-document synthesis questions and vocabulary mismatch (e.g., an employee asking about "taking time off for bereavement" when the document indexes "compassionate leave").