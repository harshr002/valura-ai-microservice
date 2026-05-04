import asyncio
import time
import statistics
import httpx


URL = "http://127.0.0.1:8000/query"

PAYLOAD = {
    "query": "How is my portfolio doing?",
    "portfolio": {
        "positions": [
            {"ticker": "NVDA", "value": 6000},
            {"ticker": "AAPL", "value": 2000},
            {"ticker": "MSFT", "value": 2000}
        ]
    },
    "conversation": []
}


async def run_once():
    start = time.perf_counter()
    first_event_time = None

    async with httpx.AsyncClient(timeout=20) as client:
        async with client.stream("POST", URL, json=PAYLOAD) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:") and first_event_time is None:
                    first_event_time = time.perf_counter()

    end = time.perf_counter()

    return {
        "first_token_latency": first_event_time - start,
        "total_latency": end - start,
    }


async def main():
    results = []

    for _ in range(20):
        results.append(await run_once())

    first_token_latencies = [r["first_token_latency"] for r in results]
    total_latencies = [r["total_latency"] for r in results]

    print("Benchmark results over 20 requests")
    print("----------------------------------")
    print(f"p95 first-token latency: {statistics.quantiles(first_token_latencies, n=20)[18]:.3f}s")
    print(f"p95 end-to-end latency: {statistics.quantiles(total_latencies, n=20)[18]:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())