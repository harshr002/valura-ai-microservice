import asyncio
import json
import os

from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse

from src.safety.guard import SafetyGuard, SafetyDecision
from src.classifier.classifier import IntentClassifier
from src.llm.mock import MockLLMClient
from src.agents.portfolio_health.agent import PortfolioHealthAgent
from src.memory.store import InMemorySessionStore


REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))

app = FastAPI(title="Valura AI Microservice")

safety_guard = SafetyGuard()
classifier = IntentClassifier(MockLLMClient())
portfolio_agent = PortfolioHealthAgent()
memory_store = InMemorySessionStore()


async def stream_response(payload: dict):
    yield {
        "event": "metadata",
        "data": json.dumps(
            {
                "agent": payload.get("agent"),
                "intent": payload.get("intent"),
                "entities": payload.get("entities", {}),
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


async def error_stream(reason: str, message: str):
    yield {
        "event": "error",
        "data": json.dumps(
            {
                "reason": reason,
                "message": message,
            }
        ),
    }

    yield {
        "event": "done",
        "data": json.dumps({"status": "failed"}),
    }


async def run_pipeline(payload: dict):
    query_text = payload.get("query", "")
    session_id = payload.get("session_id", "default")

    user_context = payload.get("user_context", {})
    portfolio = user_context.get("portfolio", payload.get("portfolio", {}))

    conversation = memory_store.get_history(session_id)
    memory_store.add_turn(session_id, "user", query_text)

    # 1. Safety Guard
    safety = safety_guard.check(query_text)

    if safety["decision"] == SafetyDecision.BLOCK.value:
        return {
            "type": "blocked",
            "reason": safety["reason"],
            "message": safety.get(
                "message",
                "This request cannot be processed for safety reasons.",
            ),
        }

    # 2. Intent Classifier
    classification = classifier.classify(query_text, conversation)

    # 3. Routed Agent
    if classification.agent == "portfolio_health":
        result = portfolio_agent.run(portfolio)

        result["agent"] = classification.agent
        result["intent"] = classification.intent
        result["entities"] = classification.entities
        result["safety_verdict"] = classification.safety_verdict

        memory_store.add_turn(session_id, "assistant", json.dumps(result))

        return {
            "type": "agent_result",
            "result": result,
        }

    # 4. Stub Agents
    response = {
        "intent": classification.intent,
        "agent": classification.agent,
        "entities": classification.entities,
        "message": "This agent is not implemented in this build.",
        "safety_verdict": classification.safety_verdict,
    }

    memory_store.add_turn(session_id, "assistant", json.dumps(response))

    return {
        "type": "stub_result",
        "result": response,
    }


@app.post("/query")
async def query(payload: dict):
    async def event_generator():
        try:
            pipeline_result = await asyncio.wait_for(
                run_pipeline(payload),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )

            if pipeline_result["type"] == "blocked":
                async for event in error_stream(
                    reason=pipeline_result["reason"],
                    message=pipeline_result["message"],
                ):
                    yield event
                return

            if pipeline_result["type"] == "agent_result":
                async for event in stream_response(pipeline_result["result"]):
                    yield event
                return

            if pipeline_result["type"] == "stub_result":
                result = pipeline_result["result"]

                yield {
                    "event": "metadata",
                    "data": json.dumps(
                        {
                            "agent": result.get("agent"),
                            "intent": result.get("intent"),
                            "entities": result.get("entities", {}),
                            "safety_verdict": result.get("safety_verdict"),
                        }
                    ),
                }

                yield {
                    "event": "message",
                    "data": json.dumps(result),
                }

                yield {
                    "event": "done",
                    "data": json.dumps({"status": "completed"}),
                }
                return

        except asyncio.TimeoutError:
            async for event in error_stream(
                reason="request_timeout",
                message=f"Request exceeded timeout of {REQUEST_TIMEOUT_SECONDS} seconds.",
            ):
                yield event

        except Exception:
            async for event in error_stream(
                reason="internal_error",
                message="The request failed safely. No internal stack trace is exposed.",
            ):
                yield event

    return EventSourceResponse(event_generator())