# Prompt Pairwise Comparison 001

**Date:** 2026-10-06  
**Judge Model:** gpt-4o  
**Candidate Model:** gpt-4o-mini  

## Tested Prompts
- **v1 (Baseline):** "You are an Enterprise Knowledge Assistant. Answer accurately based on context."
- **v2 (Variant):** "You are an Enterprise Knowledge Assistant. Answer accurately, cite relevant policy guidelines, and state clearly if information is not found."

## Result & Mitigation
- Position bias mitigated with random 50/50 order flipping.
- **v2 won 4 out of 5 runs**, demonstrating superior explicit boundary setting and policy attribution clarity.