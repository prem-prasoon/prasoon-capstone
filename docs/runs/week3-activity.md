# Week 3 Activity — /metrics endpoint

## Changes to `api/main.py`
Added an in-memory dictionary counter `request_counts`, an HTTP middleware intercepting all calls to update path counters, and a `GET /metrics` reporting endpoint.

## Sample Output
```json
{
  "endpoints": {
    "/health": 3,
    "/ask_batched": 1,
    "/ask": 1,
    "/metrics": 1
  },
  "total": 6
}