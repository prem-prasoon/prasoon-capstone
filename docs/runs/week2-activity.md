# Week 2 Activity Reflection: as_completed vs gather

## Observations
- **What `as_completed` made visible that `gather` hides:**
  `as_completed` yields tasks dynamically as each completes, exposing individual latency variations and retry delays in real time, whereas `gather` conceals this by blocking until the slowest request finishes.

- **When to reach for `gather` vs `as_completed`:**
  Use `gather` when you need all results before proceeding and must preserve original input order, and use `as_completed` when streaming responses immediately to a user interface or halting early on the first successful match.