class MockLLMClient:
    """
    Deterministic mock for testing.
    """

    def classify(self, query: str, conversation):
        q = query.lower()

        if "portfolio" in q or "health" in q:
            return {
                "intent": "portfolio_health",
                "agent": "portfolio_health",
                "entities": {},
                "safety_verdict": "ok",
            }

        return {
            "intent": "general_question",
            "agent": "support",
            "entities": {},
            "safety_verdict": "ok",
        }