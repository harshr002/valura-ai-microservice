from src.agents.portfolio_health.agent import PortfolioHealthAgent


def test_empty_portfolio_handled():
    agent = PortfolioHealthAgent()
    result = agent.run({})
    assert result["observations"]
    assert "don’t have any investments yet" in result["observations"][0]["text"]


def test_concentrated_portfolio_flagged():
    agent = PortfolioHealthAgent()
    portfolio = {
        "positions": [
            {"ticker": "NVDA", "value": 6000},
            {"ticker": "AAPL", "value": 2000},
            {"ticker": "MSFT", "value": 2000},
        ]
    }
    result = agent.run(portfolio)
    assert result["concentration_risk"]["flag"] == "high"