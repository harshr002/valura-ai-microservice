# Valura AI Microservice — Team Lead Assignment

## Overview

This repository implements the core spine of Valura’s AI microservice.

The system is designed as a safety-first, streaming AI architecture that helps novice investors:

- Build
- Monitor
- Grow
- Protect

This submission implements:

- Deterministic Safety Guard
- Single-call Intent Classifier
- Portfolio Health Check Agent
- FastAPI + Server-Sent Events (SSE)
- In-memory session memory
- CI-safe mocked LLM testing

---

# Architecture

## Request Flow

```text
Client Request
     ↓
Safety Guard
     ↓
Intent Classifier
     ↓
Agent Router
     ↓
Portfolio Health Agent / Stub Agent
     ↓
SSE Streaming Response
```

Design goal:

Build a spine that can scale to multiple agents without rewrites.

---

# Library Choices

## FastAPI

Chosen because:

- Async-first
- Lightweight
- Production-ready
- Excellent for microservices

## sse-starlette

Chosen because:

- Native SSE support
- Clean FastAPI integration
- Minimal overhead

## Pydantic

Chosen because:

- Strong schema validation
- Structured LLM outputs
- Safer routing boundaries

## Pytest

Chosen because:

- CI-friendly
- Fast feedback loop
- Easy mocking

---

# Component 1 — Safety Guard

The Safety Guard is:

- Fully deterministic
- Local-only
- No network calls
- No LLM calls
- Designed for sub-10ms execution

Blocked categories:

- Insider trading
- Market manipulation
- Money laundering
- Guaranteed-return claims
- Reckless leverage

Educational queries are allowed.

## Safety Precedence

Safety always runs before classification.

If the safety layer blocks a request:

- The classifier is never called
- The request is terminated safely

The classifier safety verdict is informational only.

Only the safety guard has blocking authority.

## Tradeoff

In ambiguous cases, this implementation intentionally prefers over-blocking over unsafe financial guidance.

---

# Component 2 — Intent Classifier

The classifier performs exactly one LLM call.

Output schema:

```json
{
  "intent": "portfolio_health",
  "agent": "portfolio_health",
  "entities": {
    "tickers": ["AAPL"]
  },
  "safety_verdict": "ok"
}
```

The classifier returns:

- Intent
- Extracted entities
- Target agent
- Informational safety verdict

## Failure Handling

If the LLM fails:

- The pipeline does not crash
- Fallback agent = `support`

## Follow-up Handling

Conversation memory allows:

```text
User: Tell me about Microsoft
User: What about Apple?
```

The classifier resolves entity carry-over across turns.

---

# Component 3 — Portfolio Health Agent

This agent handles:

- Concentration risk
- Performance metrics
- Benchmark comparison
- Actionable novice-friendly observations

The agent receives portfolio data as input.

It does not fetch portfolio data itself.

## Empty Portfolio Handling

If a user has no holdings:

The system returns BUILD-oriented guidance instead of errors.

## Benchmarks

Benchmark is selected by market:

| Market | Benchmark |
|--------|------------|
| US | S&P 500 |
| India | NIFTY 50 |
| EU | STOXX Europe 600 |
| Global | MSCI World |

Every response includes a regulatory disclaimer.

---

# Stub Agent Contract

Only Portfolio Health is fully implemented.

Other agents:

- market_research
- investment_strategy
- financial_calculator
- support

Return structured stub responses containing:

- Intent
- Extracted entities
- Agent name
- Not-implemented message

The router never crashes when routing to an unimplemented agent.

---

# Session Memory

## In-Memory Store

Chosen because:

- No infrastructure dependencies
- Fastest demo implementation
- Easy testing

Tradeoff:

Memory resets when the service restarts.

With more time:

Would migrate to:

- PostgreSQL
or
- SQLite

---

# Streaming

Responses are streamed using SSE.

Event types:

## Metadata

```text
event: metadata
```

## Message

```text
event: message
```

## Completion

```text
event: done
```

---

# Timeout and Error Handling

The full request pipeline is wrapped in:

```python
asyncio.wait_for(...)
```

Timeout:

```text
15 seconds
```

Why 15 seconds?

- Prevents hanging requests
- Protects server resources
- Well below assignment limits

Timeouts return:

```text
event: error
data: {"reason": "request_timeout"}
```

Internal exceptions also return structured SSE error events.

No stack traces are exposed.

---

# Testing Strategy

All tests run under:

```bash
pytest tests/ -v
```

LLM is fully mocked.

CI does not require:

```text
OPENAI_API_KEY
```

---

# Testing Contract

## Routing Match

Agent names must match exactly.

Example:

```text
portfolio_health == portfolio_health
```

## Entity Matching

Uses subset matching.

Extra entities are allowed.

## Ticker Normalization

Normalization rules:

```text
AAPL == aapl
ASML == ASML.AS
```

## Numeric Matching

Tolerance:

```text
±5%
```

Applied to:

- amount
- rate
- period_years

---

# Evaluation Results

Measured using:

```bash
pytest tests/ -v -s
```

Current results:

```text
Classifier routing accuracy: 100.0%
Safety harmful recall: 100.0%
Educational pass-through: 100.0%
Empty portfolio handling: PASS
```

---

# Cost & Performance

## Development Model

gpt-4o-mini

## Evaluation Model

gpt-4.1

## Measurement Method

Measured using:

```bash
python scripts/benchmark.py
```

Benchmark sends 20 SSE requests.

Measures:

- Request → first token
- Request → completion

## Results

Paste your measured output:

```text
p95 first-token latency: 0.xxxs
p95 end-to-end latency: x.xxxs
```

## Cost Control Strategy

Cost is minimized through:

- Safety guard before LLM
- Exactly one classifier call
- No agent-side LLM calls

Estimated query cost stays under assignment target.

---

# Environment Variables

Documented in:

```text
.env.example
```

Example:

```env
OPENAI_API_KEY=your_api_key_here
REQUEST_TIMEOUT_SECONDS=15
```

`.env` is gitignored.

---

# Setup

## Create environment

```bash
python -m venv .venv
source .venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run service

```bash
uvicorn src.api.app:app --reload
```

---

# Future Improvements

With another week I would add:

- Live market data integration via yfinance
- Embedding-based pre-classifier
- Query dedupe cache
- Tenant-based model selection
- Rate limiting
- Persistent storage

---

# Defence Video

Paste your Loom / YouTube link here:

VIDEO_LINK_HERE

---

# Repository

Paste your GitHub repository link here:

REPO_LINK_HERE