from src.classifier.classifier import IntentClassifier
from src.llm.mock import MockLLMClient


def test_portfolio_health_routed():
    classifier = IntentClassifier(MockLLMClient())
    result = classifier.classify("How is my portfolio doing?", [])
    assert result.agent == "portfolio_health"


def test_market_research_routed_with_ticker_followup():
    classifier = IntentClassifier(MockLLMClient())
    result = classifier.classify(
        "what about Apple?",
        [{"role": "user", "content": "Tell me about Microsoft stock"}],
    )
    assert result.agent == "market_research"
    assert "AAPL" in result.entities["tickers"]


def test_fallback_on_error():
    class BrokenLLM:
        def classify(self, q, c):
            raise RuntimeError("boom")

    classifier = IntentClassifier(BrokenLLM())
    result = classifier.classify("Anything", [])
    assert result.agent == "support"