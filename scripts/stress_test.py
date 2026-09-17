"""scripts/stress_test.py — Parallel load tester for the FastAPI endpoint."""
import argparse
import asyncio
import time
import httpx


async def send_request(client: httpx.AsyncClient, semaphore: asyncio.Semaphore, url: str) -> float | None:
    async with semaphore:
        t0 = time.perf_counter()
        try:
            resp = await client.post(url, json={"question": "What is RAG?"}, timeout=120.0)
            if resp.status_code == 200:
                return time.perf_counter() - t0
        except Exception as e:
            print(f"Request failed: {e}")
        return None


async def run_stress(total_requests: int, concurrency: int, url: str):
    semaphore = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient() as client:
        start_time = time.perf_counter()
        tasks = [send_request(client, semaphore, url) for _ in range(total_requests)]
        latencies = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time

    successful = [l for l in latencies if l is not None]
    successful.sort()

    print(f"\nStress test: {total_requests} requests, up to {concurrency} concurrent")
    print("─" * 60)
    print(f"Total wall time:   {total_time:.2f}s")
    print(f"Successes:         {len(successful)} / {total_requests}")
    if successful:
        p50 = successful[int(len(successful) * 0.50)]
        p95 = successful[int(len(successful) * 0.95)]
        print(f"Effective req/s:   {len(successful) / total_time:.2f}")
        print("\nLatency (successful requests):")
        print(f"  min:   {min(successful):.2f}s")
        print(f"  p50:   {p50:.2f}s")
        print(f"  p95:   {p95:.2f}s")
        print(f"  max:   {max(successful):.2f}s\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", type=int, default=10)
    parser.add_argument("--concurrent", type=int, default=3)
    parser.add_argument("--url", type=str, default="http://localhost:8000/ask")
    args = parser.parse_args()

    asyncio.run(run_stress(args.requests, args.concurrent, args.url))