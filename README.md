# Valura AI Microservice — Team Lead Assignment

## Overview

This repository implements the core spine of Valura’s AI microservice: a safety-first, streaming AI system that classifies user intent, routes queries to specialist agents, and returns real-time responses via Server-Sent Events (SSE).

The system is designed with novice investors in mind, prioritizing:
- deterministic safety
- low latency
- predictable cost
- clear, actionable outputs

This submission implements:
- A deterministic financial safety guard
- A single-call intent classifier with structured output
- A fully implemented Portfolio Health Check agent
- A FastAPI HTTP layer with SSE streaming
- CI-safe tests with a mocked LLM client

---

## Architecture

**Request flow:**

1. **Safety Guard (local, deterministic)**  
   Runs synchronously before any LLM call. Blocks insider trading, guaranteed returns, market manipulation, money laundering, and reckless leverage.

2. **Intent Classifier (single LLM call)**  
   Classifies intent, extracts entities, selects the target agent, and emits an informational safety verdict.  
   - LLM-backed in production  
   - Fully mocked in tests for CI safety

3. **Agent Router**
   Dispatches to the correct specialist agent.
   - Portfolio Health Agent is fully implemented
   - All other agents return a structured “not implemented” stub

4. **Streaming Response Layer**
   Responses are streamed to the client using Server-Sent Events (SSE).

---

## Safety Design

Safety is enforced in two layers:

- **Authoritative Safety Guard**  
  Deterministic regex-based filter that blocks disallowed financial actions with category-specific reasons.

- **Informational Safety Verdict**  
  Returned by the classifier for observability and logging only. It does not affect routing or blocking.

Educational queries about restricted topics are allowed by design.

---

## Intent Classification

- One LLM call per request
- Structured output enforced via Pydantic
- Handles follow-up queries using conversation context
- Safe fallback behavior on LLM failure (never crashes the pipeline)

---

## Portfolio Health Check Agent

The Portfolio Health agent analyzes:
- concentration risk
- basic performance metrics
- benchmark comparison
- novice-friendly observations

Edge cases:
- Users with empty portfolios receive a BUILD-oriented response instead of an error.

Every response includes a regulatory disclaimer.

---

## Streaming (SSE)

- All responses stream via SSE
- Metadata is sent first, followed by message chunks, then a completion event
- Errors are returned as structured SSE error events (no stack traces)

---

## Cost & Performance

- Development model: `gpt-4o-mini`
- Evaluation model: `gpt-4.1`
- Single LLM call per request
- Deterministic safety guard avoids unnecessary LLM calls

Latency was measured locally using timestamped logs:
- First-token streaming latency: ~<1s (local)
- End-to-end completion: ~<3s (local, mocked LLM)

Projected cost per query at `gpt-4.1` pricing is under $0.05.

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt