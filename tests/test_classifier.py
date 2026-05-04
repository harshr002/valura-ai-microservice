from src.classifier.classifier import IntentClassifier
from src.llm.mock import MockLLMClient


def normalize_ticker(ticker: str):
    """
    Normalization:
    AAPL == aapl
    ASML == ASML.AS
    """
    ticker = ticker.upper()
    ticker = ticker.split(".")[0]
    return ticker


def entity_subset_match(expected_entities: dict, actual_entities: dict):
    for key, expected_values in expected_entities.items():
        actual_values = actual_entities.get(key, [])

        normalized_expected = {
            normalize_ticker(v) if isinstance(v, str) else v
            for v in expected_values
        }

        normalized_actual = {
            normalize_ticker(v) if isinstance(v, str) else v
            for v in actual_values
        }

        if not normalized_expected.issubset(normalized_actual):
            return False

    return True


def numeric_match(expected, actual):
    """
    ±5% tolerance
    """
    if expected == 0:
        return actual == 0

    tolerance = abs(expected) * 0.05

    return abs(expected - actual) <= tolerance


def test_portfolio_health_routed():
    classifier = IntentClassifier(MockLLMClient())

    result = classifier.classify(
        "How is my portfolio doing?",
        [],
    )

    assert result.agent == "portfolio_health"


def test_followup_market_research():
    classifier = IntentClassifier(MockLLMClient())

    result = classifier.classify(
        "what about Apple?",
        [
            {
                "role": "user",
                "content": "Tell me about Microsoft stock",
            }
        ],
    )

    assert result.agent == "market_research"

    expected_entities = {
        "tickers": ["AAPL"]
    }

    assert entity_subset_match(
        expected_entities,
        result.entities,
    )


def test_ticker_normalization():
    expected_entities = {
        "tickers": ["ASML"]
    }

    actual_entities = {
        "tickers": ["ASML.AS"]
    }

    assert entity_subset_match(
        expected_entities,
        actual_entities,
    )


def test_numeric_match():
    assert numeric_match(100, 104)
    assert numeric_match(100, 96)
    assert not numeric_match(100, 120)


def test_fallback_on_error():
    class BrokenLLM:
        def classify(self, q, c):
            raise RuntimeError("boom")

    classifier = IntentClassifier(BrokenLLM())

    result = classifier.classify(
        "Anything",
        [],
    )

    assert result.agent == "support"