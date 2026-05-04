from typing import List
from backend.classifier.schema import ClassifiedIntent


class IntentClassifier:
    """
    Single-call intent classifier.
    LLM-backed in prod, mocked in tests.
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def classify(self, query: str, conversation: List[str]) -> ClassifiedIntent:
        try:
            response = self.llm_client.classify(query, conversation)
            return ClassifiedIntent(**response)
        except Exception:
            # Safe fallback — do not crash the pipeline
            return ClassifiedIntent(
                intent="unknown",
                agent="support",
                entities={},
                safety_verdict="classifier_error",
            )