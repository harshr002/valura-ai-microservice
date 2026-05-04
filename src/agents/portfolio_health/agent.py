from typing import Dict, List


class PortfolioHealthAgent:
    """
    Portfolio health analysis for novice investors.

    Uses only passed-in portfolio data.
    No market-data fetching inside the agent.
    """

    DISCLAIMER = (
        "This is not investment advice. It is an educational portfolio health summary. "
        "Please consult a qualified financial adviser before making investment decisions."
    )

    MARKET_BENCHMARKS = {
        "US": "S&P 500",
        "USA": "S&P 500",
        "INDIA": "NIFTY 50",
        "IN": "NIFTY 50",
        "EU": "STOXX Europe 600",
        "GLOBAL": "MSCI World",
    }

    def run(self, portfolio: Dict) -> Dict:
        if not portfolio or not portfolio.get("positions"):
            return {
                "concentration_risk": {
                    "top_position_pct": 0,
                    "top_3_positions_pct": 0,
                    "flag": "none",
                },
                "performance": {
                    "total_return_pct": 0,
                    "annualized_return_pct": 0,
                },
                "benchmark_comparison": {
                    "benchmark": self._select_benchmark(portfolio),
                    "portfolio_return_pct": 0,
                    "benchmark_return_pct": None,
                    "alpha_pct": None,
                },
                "observations": [
                    {
                        "severity": "info",
                        "text": (
                            "You don’t have any investments yet. That is a good starting point: "
                            "first define your goal, time horizon, emergency fund, and risk comfort before choosing assets."
                        ),
                    },
                    {
                        "severity": "info",
                        "text": (
                            "For a first allocation, a novice investor should usually start with broad diversification "
                            "instead of putting most money into one stock."
                        ),
                    },
                ],
                "disclaimer": self.DISCLAIMER,
            }

        positions = portfolio["positions"]
        total_value = sum(float(p.get("value", 0)) for p in positions)

        if total_value <= 0:
            return self.run({})

        sorted_positions = sorted(
            positions,
            key=lambda p: float(p.get("value", 0)),
            reverse=True,
        )

        top_position = sorted_positions[0]
        top_position_pct = round(float(top_position.get("value", 0)) / total_value * 100, 1)
        top_3_positions_pct = round(
            sum(float(p.get("value", 0)) for p in sorted_positions[:3]) / total_value * 100,
            1,
        )

        concentration_flag = self._concentration_flag(top_position_pct, top_3_positions_pct)

        total_cost = sum(float(p.get("cost_basis", p.get("value", 0))) for p in positions)
        total_return_pct = 0.0
        if total_cost > 0:
            total_return_pct = round(((total_value - total_cost) / total_cost) * 100, 1)

        holding_years = float(portfolio.get("holding_period_years", 1))
        annualized_return_pct = self._annualized_return(total_return_pct, holding_years)

        benchmark = self._select_benchmark(portfolio)
        benchmark_return_pct = portfolio.get("benchmark_return_pct")
        alpha_pct = None
        if benchmark_return_pct is not None:
            alpha_pct = round(total_return_pct - float(benchmark_return_pct), 1)

        observations = []

        observations.append(
            {
                "severity": "warning" if concentration_flag == "high" else "info",
                "text": (
                    f"Your largest holding is {top_position.get('ticker', 'one asset')} "
                    f"at {top_position_pct}% of the portfolio. "
                    f"This is {concentration_flag} concentration risk."
                ),
            }
        )

        if top_3_positions_pct >= 70:
            observations.append(
                {
                    "severity": "warning",
                    "text": (
                        f"Your top 3 holdings make up {top_3_positions_pct}% of the portfolio. "
                        "That means a few assets drive most of your outcome."
                    ),
                }
            )

        if alpha_pct is not None:
            if alpha_pct >= 0:
                observations.append(
                    {
                        "severity": "info",
                        "text": (
                            f"Your portfolio is ahead of {benchmark} by {alpha_pct}% over the measured period."
                        ),
                    }
                )
            else:
                observations.append(
                    {
                        "severity": "info",
                        "text": (
                            f"Your portfolio is behind {benchmark} by {abs(alpha_pct)}% over the measured period."
                        ),
                    }
                )
        else:
            observations.append(
                {
                    "severity": "info",
                    "text": (
                        f"{benchmark} is used as the relevant benchmark based on the user market. "
                        "Benchmark return was not supplied, so alpha is not calculated."
                    ),
                }
            )

        observations.append(
            {
                "severity": "info",
                "text": (
                    "A practical next step is to check whether your largest positions still match your risk profile "
                    "and whether you need broader diversification."
                ),
            }
        )

        return {
            "concentration_risk": {
                "top_position_pct": top_position_pct,
                "top_3_positions_pct": top_3_positions_pct,
                "flag": concentration_flag,
            },
            "performance": {
                "total_return_pct": total_return_pct,
                "annualized_return_pct": annualized_return_pct,
            },
            "benchmark_comparison": {
                "benchmark": benchmark,
                "portfolio_return_pct": total_return_pct,
                "benchmark_return_pct": benchmark_return_pct,
                "alpha_pct": alpha_pct,
            },
            "observations": observations,
            "disclaimer": self.DISCLAIMER,
        }

    def _concentration_flag(self, top_position_pct: float, top_3_positions_pct: float) -> str:
        if top_position_pct >= 50 or top_3_positions_pct >= 80:
            return "high"
        if top_position_pct >= 30 or top_3_positions_pct >= 60:
            return "medium"
        return "low"

    def _annualized_return(self, total_return_pct: float, years: float) -> float:
        if years <= 0:
            return total_return_pct
        total_return_decimal = total_return_pct / 100
        annualized = ((1 + total_return_decimal) ** (1 / years) - 1) * 100
        return round(annualized, 1)

    def _select_benchmark(self, portfolio: Dict) -> str:
        if not portfolio:
            return "MSCI World"

        market = str(
            portfolio.get("market")
            or portfolio.get("country")
            or portfolio.get("base_market")
            or "GLOBAL"
        ).upper()

        return self.MARKET_BENCHMARKS.get(market, "MSCI World")