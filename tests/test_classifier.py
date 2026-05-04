from backend.classifier.classifier import IntentClassifier
from backend.llm.mock import MockLLMClient


def test_portfolio_health_routed():
    classifier = IntentClassifier(MockLLMClient())
    result = classifier.classify("How is my portfolio doing?", [])
    assert result.agent == "portfolio_health"


def test_fallback_on_error():
    class BrokenLLM:
        def classify(self, q, c):
            raise RuntimeError("boom")

    classifier = IntentClassifier(BrokenLLM())
    result = classifier.classify("Anything", [])
    assert result.agent == "support"