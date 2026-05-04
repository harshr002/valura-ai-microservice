import re


class MockLLMClient:
    """
    Deterministic mock classifier for tests and CI.
    No OPENAI_API_KEY required.
    """

    TICKER_PATTERN = re.compile(r"\b[A-Z]{1,5}(?:\.[A-Z]{1,3})?\b")

    def classify(self, query: str, conversation):
        q = query.lower()

        tickers = self.TICKER_PATTERN.findall(query)

        if "apple" in q:
            tickers.append("AAPL")
        if "microsoft" in q:
            tickers.append("MSFT")
        if "nvidia" in q:
            tickers.append("NVDA")
        if "tesla" in q:
            tickers.append("TSLA")

        tickers = list(set(tickers))

        if q.strip() in {
            "what about apple?",
            "what about apple",
            "and apple?",
            "apple?",
            "what about microsoft?",
            "what about microsoft",
        }:
            return {
                "intent": "market_research",
                "agent": "market_research",
                "entities": {"tickers": tickers},
                "safety_verdict": "ok",
            }

        if any(
            word in q
            for word in [
                "portfolio",
                "health check",
                "diversified",
                "diversification",
            ]
        ):
            return {
                "intent": "portfolio_health",
                "agent": "portfolio_health",
                "entities": {"tickers": tickers},
                "safety_verdict": "ok",
            }

        if any(
            word in q
            for word in [
                "calculate",
                "compound",
                "return",
                "interest",
                "sip",
            ]
        ):
            return {
                "intent": "financial_calculation",
                "agent": "financial_calculator",
                "entities": {"tickers": tickers},
                "safety_verdict": "ok",
            }

        if any(
            word in q
            for word in [
                "buy",
                "invest",
                "rebalance",
                "strategy",
                "allocation plan",
                "allocation strategy",
            ]
        ):
            return {
                "intent": "investment_strategy",
                "agent": "investment_strategy",
                "entities": {"tickers": tickers},
                "safety_verdict": "ok",
            }

        if any(
            word in q
            for word in [
                "news",
                "research",
                "market",
                "stock",
                "earnings",
                "price",
                "apple",
                "microsoft",
            ]
        ):
            return {
                "intent": "market_research",
                "agent": "market_research",
                "entities": {"tickers": tickers},
                "safety_verdict": "ok",
            }

        return {
            "intent": "support",
            "agent": "support",
            "entities": {"tickers": tickers},
            "safety_verdict": "ok",
        }