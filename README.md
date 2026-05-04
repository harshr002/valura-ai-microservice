# Valura AI Microservice — Team Lead Assignment

## Overview

This repository implements the core spine of Valura’s AI microservice.

The goal is to demonstrate how a safety-first, streaming AI architecture can:

- protect users from harmful financial actions
- classify financial intent in one structured LLM call
- route requests to specialist agents
- stream novice-friendly outputs in real time

This build implements:

- Deterministic Safety Guard
- Single-call Intent Classifier
- Portfolio Health Check Agent
- FastAPI + SSE streaming layer
- Session memory (in-memory for demo)
- Fully mocked LLM in tests (CI-safe)

---

## Architecture

### Request Flow

Every request follows this pipeline:

```text
User Request
     ↓
Safety Guard (deterministic, local)
     ↓
Intent Classifier (single structured LLM call)
     ↓
Agent Router
     ↓
Portfolio Health Agent / Stub Agent
     ↓
SSE Stream Response
```

The design goal was extensibility without rewrites.

---

## Why These Libraries

### FastAPI

Used because:

- async-first
- lightweight
- production-ready
- excellent ecosystem for microservices

### sse-starlette

Used because:

- simple SSE support
- integrates cleanly with FastAPI
- low overhead

### Pydantic

Used because:

- schema enforcement
- structured outputs
- safer routing boundaries

### Pytest

Used because:

- CI compatibility
- fast test iteration
- simple mocking support

---

# Component 1 — Safety Guard

The safety guard is:

- deterministic
- local-only
- no network
- no LLM
- designed for sub-10ms execution

Blocked categories:

- insider trading
- market manipulation
- money laundering
- guaranteed-return claims
- reckless leverage

Educational queries are allowed.

### Tradeoff

The safety layer intentionally prioritizes user protection over perfect recall.

In ambiguous cases, over-blocking is preferred over unsafe guidance.

This reflects financial-system safety priorities.

---

# Component 2 — Intent Classifier

The classifier performs exactly **one LLM call**.

Structured output contains:

- intent
- agent
- entities
- informational safety verdict

Example:

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

### Failure Handling

If the classifier fails:

- request does not crash
- fallback agent = `support`

### Conversation Handling

Session memory allows follow-up resolution:

Example:

```text
User: Tell me about Microsoft
User: What about Apple?
```

The classifier uses prior turns to resolve follow-up references.

---

# Component 3 — Portfolio Health Agent

The Portfolio Health agent handles:

- concentration risk
- performance metrics
- benchmark comparison
- novice-friendly observations

Portfolio is passed into the pipeline:

The agent does **not fetch portfolio data itself.**

### Empty Portfolio Handling

For users with no holdings:

The agent does not error.

Instead, it returns BUILD-oriented guidance.

### Benchmarks

Benchmarks are selected by market:

| Market | Benchmark |
|--------|------------|
| US | S&P 500 |
| India | NIFTY 50 |
| EU | STOXX Europe 600 |
| Global | MSCI World |

---

# Session Memory

Persistence choice:

## In-Memory Session Store

Chosen because:

- simplest demo implementation
- zero external infrastructure
- sufficient for assignment scope

Tradeoff:

Memory resets on restart.

With more time:

Would migrate to:

- PostgreSQL
or
- SQLite

---

# Streaming

Responses are streamed using SSE.

Event types:

### Metadata

```text
event: metadata
```

### Message

```text
event: message
```

### Completion

```text
event: done
```

---

# Timeout and Error Handling

The entire pipeline is wrapped in:

```python
asyncio.wait_for(...)
```

Timeout:

```text
15 seconds
```

Why 15 seconds?

Because:

- protects system resources
- prevents hanging client connections
- well below assignment targets

Timeouts return structured SSE errors:

```text
event: error
data: {"reason": "request_timeout"}
```

Internal errors also return structured SSE responses.

No stack traces are exposed.

---

# Cost & Performance

## Development Model

OpenAI lightweight chat model (`gpt-4o-mini` equivalent)

## Evaluation Assumption

GPT-4-class production model

---

## Measurement Method

Measured using:

```bash
python scripts/benchmark.py
```

The benchmark sends 20 SSE requests and measures:

- request → first token
- request → completion

### Measured Results

Paste your actual benchmark output here:

```text
p95 first-token latency: 0.xxxs
p95 end-to-end latency: x.xxxs
```

---

## Cost Strategy

Cost is controlled through:

- safety guard before LLM
- exactly one classifier call
- no agent-side LLM calls

Projected query cost remains under assignment target.

---

# Fixtures

The system is designed to work with:

- user profiles
- conversation transcripts
- safety datasets
- intent classification datasets

Portfolio and user data are passed through request payloads.

No user portfolio is hardcoded.

No market prices are hardcoded.

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

Tests do not require this.

---

# Setup

Create environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn src.api.app:app --reload
```

---

# Testing
# Test Matcher Rules

## Routing Match

The classifier output agent must exactly match:

expected_agent

Example:

portfolio_health == portfolio_health

---

## Entity Match

Entity matching uses subset logic.

Expected entities must exist in actual output.

Extra extracted entities are allowed.

---

## Ticker Normalization

Tickers are normalized:

AAPL == aapl  
ASML == ASML.AS

Normalization rule:

- uppercase
- ignore exchange suffix

---

## Numeric Match

Numeric fields:

- amount
- rate
- period_years

Tolerance:

±5%

---

# Future Improvements

With one more week I would add:

- live market data via yfinance
- embedding-based pre-classifier
- model caching
- multi-tenant rate limiting
- persistent storage

---

# Defence Video

Loom / YouTube (Unlisted):

PASTE VIDEO LINK HERE


---

# Repository

GitHub Repository:

PASTE GITHUB LINK HERE