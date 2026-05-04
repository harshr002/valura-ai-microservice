from typing import Dict, List


class PortfolioHealthAgent:
    """
    Analyzes portfolio health for novice investors.
    """

    DISCLAIMER = "This is not investment advice. For educational purposes only."

    def run(self, portfolio: Dict) -> Dict:
        # Handle empty portfolio
        if not portfolio or not portfolio.get("positions"):
            return {
                "concentration_risk": None,
                "performance": None,
                "benchmark_comparison": None,
                "observations": [
                    {
                        "severity": "info",
                        "text": "You don’t have any investments yet. This is a good time to think about your goals, time horizon, and risk tolerance before making your first allocation.",
                    }
                ],
                "disclaimer": self.DISCLAIMER,
            }

        positions = portfolio["positions"]
        total_value = sum(p["value"] for p in positions)

        # Concentration analysis
        sorted_positions = sorted(
            positions, key=lambda x: x["value"], reverse=True
        )

        top_position_pct = round(
            (sorted_positions[0]["value"] / total_value) * 100, 1
        )
        top_3_value = sum(p["value"] for p in sorted_positions[:3])
        top_3_positions_pct = round((top_3_value / total_value) * 100, 1)

        concentration_flag = "low"
        if top_position_pct > 50:
            concentration_flag = "high"
        elif top_position_pct > 30:
            concentration_flag = "medium"

        observations = []

        if concentration_flag == "high":
            observations.append(
                {
                    "severity": "warning",
                    "text": f"{top_position_pct}% of your portfolio is in a single position, which increases risk if that asset performs poorly.",
                }
            )

        # Placeholder performance numbers (mocked for now)
        performance = {
            "total_return_pct": 10.0,
            "annualized_return_pct": 8.0,
        }

        benchmark_comparison = {
            "benchmark": "S&P 500",
            "portfolio_return_pct": 10.0,
            "benchmark_return_pct": 9.0,
            "alpha_pct": 1.0,
        }

        if benchmark_comparison["alpha_pct"] > 0:
            observations.append(
                {
                    "severity": "info",
                    "text": "Your portfolio has slightly outperformed the benchmark over the measured period.",
                }
            )

        return {
            "concentration_risk": {
                "top_position_pct": top_position_pct,
                "top_3_positions_pct": top_3_positions_pct,
                "flag": concentration_flag,
            },
            "performance": performance,
            "benchmark_comparison": benchmark_comparison,
            "observations": observations,
            "disclaimer": self.DISCLAIMER,
        }