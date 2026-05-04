from src.agents.portfolio_health.agent import PortfolioHealthAgent


def test_empty_portfolio_handled():
    agent = PortfolioHealthAgent()
    result = agent.run({})
    assert result["observations"]
    assert "don’t have any investments yet" in result["observations"][0]["text"]
    assert result["disclaimer"]


def test_concentrated_portfolio_flagged():
    agent = PortfolioHealthAgent()
    portfolio = {
        "market": "US",
        "benchmark_return_pct": 9.0,
        "holding_period_years": 1,
        "positions": [
            {"ticker": "NVDA", "value": 6000, "cost_basis": 4000},
            {"ticker": "AAPL", "value": 2000, "cost_basis": 1800},
            {"ticker": "MSFT", "value": 2000, "cost_basis": 2200},
        ],
    }
    result = agent.run(portfolio)
    assert result["concentration_risk"]["flag"] == "high"
    assert result["performance"]["total_return_pct"] > 0
    assert result["benchmark_comparison"]["benchmark"] == "S&P 500"
    assert result["benchmark_comparison"]["alpha_pct"] is not None


def test_india_market_uses_nifty_benchmark():
    agent = PortfolioHealthAgent()
    portfolio = {
        "market": "India",
        "positions": [
            {"ticker": "RELIANCE", "value": 5000, "cost_basis": 4500},
            {"ticker": "INFY", "value": 5000, "cost_basis": 4800},
        ],
    }
    result = agent.run(portfolio)
    assert result["benchmark_comparison"]["benchmark"] == "NIFTY 50"