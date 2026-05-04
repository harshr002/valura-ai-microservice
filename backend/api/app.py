from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import json
import asyncio

from backend.safety.guard import SafetyGuard, SafetyDecision
from backend.classifier.classifier import IntentClassifier
from backend.llm.mock import MockLLMClient
from backend.agents.portfolio_health.agent import PortfolioHealthAgent

app = FastAPI(title="Valura AI Microservice")

safety_guard = SafetyGuard()
classifier = IntentClassifier(MockLLMClient())
portfolio_agent = PortfolioHealthAgent()


async def stream_response(payload: dict):
    """
    Streams response chunks as SSE events.
    """
    yield {
        "event": "metadata",
        "data": json.dumps(
            {
                "agent": payload.get("agent"),
                "intent": payload.get("intent"),
                "safety_verdict": payload.get("safety_verdict"),
            }
        ),
    }

    # Simulate streaming chunks
    for observation in payload.get("observations", []):
        await asyncio.sleep(0.2)
        yield {
            "event": "message",
            "data": json.dumps(observation),
        }

    yield {
        "event": "done",
        "data": json.dumps({"status": "completed"}),
    }


@app.post("/query")
async def query(payload: dict):
    query_text = payload.get("query", "")
    portfolio = payload.get("portfolio", {})
    conversation = payload.get("conversation", [])

    # 1. Safety Guard (authoritative)
    safety = safety_guard.check(query_text)
    if safety["decision"] == SafetyDecision.BLOCK.value:
        async def blocked():
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "reason": safety["reason"],
                        "message": "This request cannot be processed for safety reasons.",
                    }
                ),
            }

        return EventSourceResponse(blocked())

    # 2. Intent Classification
    classification = classifier.classify(query_text, conversation)

    # 3. Routing
    if classification.agent == "portfolio_health":
        result = portfolio_agent.run(portfolio)
        result["agent"] = classification.agent
        result["intent"] = classification.intent
        result["safety_verdict"] = classification.safety_verdict
        return EventSourceResponse(stream_response(result))

    # 4. Stub for unimplemented agents
    async def not_implemented():
        yield {
            "event": "message",
            "data": json.dumps(
                {
                    "intent": classification.intent,
                    "agent": classification.agent,
                    "entities": classification.entities,
                    "message": "This agent is not implemented in this build.",
                }
            ),
        }
        yield {"event": "done", "data": "{}"}

    return EventSourceResponse(not_implemented())