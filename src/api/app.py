import asyncio
import json

from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse

from src.safety.guard import SafetyGuard, SafetyDecision
from src.classifier.classifier import IntentClassifier
from src.llm.mock import MockLLMClient
from src.agents.portfolio_health.agent import PortfolioHealthAgent
from src.memory.store import InMemorySessionStore


app = FastAPI(title="Valura AI Microservice")

safety_guard = SafetyGuard()
classifier = IntentClassifier(MockLLMClient())
portfolio_agent = PortfolioHealthAgent()
memory_store = InMemorySessionStore()


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
    session_id = payload.get("session_id", "default")

    user_context = payload.get("user_context", {})
    portfolio = user_context.get("portfolio", payload.get("portfolio", {}))

    conversation = memory_store.get_history(session_id)
    memory_store.add_turn(session_id, "user", query_text)

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
            yield {
                "event": "done",
                "data": json.dumps({"status": "blocked"}),
            }

        return EventSourceResponse(blocked())

    classification = classifier.classify(query_text, conversation)

    if classification.agent == "portfolio_health":
        result = portfolio_agent.run(portfolio)

        result["agent"] = classification.agent
        result["intent"] = classification.intent
        result["entities"] = classification.entities
        result["safety_verdict"] = classification.safety_verdict

        memory_store.add_turn(session_id, "assistant", json.dumps(result))

        return EventSourceResponse(stream_response(result))

    async def not_implemented():
        response = {
            "intent": classification.intent,
            "agent": classification.agent,
            "entities": classification.entities,
            "message": "This agent is not implemented in this build.",
        }

        memory_store.add_turn(session_id, "assistant", json.dumps(response))

        yield {
            "event": "metadata",
            "data": json.dumps(
                {
                    "agent": classification.agent,
                    "intent": classification.intent,
                    "safety_verdict": classification.safety_verdict,
                }
            ),
        }

        yield {
            "event": "message",
            "data": json.dumps(response),
        }

        yield {
            "event": "done",
            "data": json.dumps({"status": "completed"}),
        }

    return EventSourceResponse(not_implemented())