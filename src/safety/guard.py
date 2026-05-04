from enum import Enum
import re
from typing import Dict


class SafetyDecision(Enum):
    ALLOW = "allow"
    BLOCK = "block"


class SafetyCategory(Enum):
    INSIDER_TRADING = "insider_trading"
    GUARANTEED_RETURNS = "guaranteed_returns"
    MARKET_MANIPULATION = "market_manipulation"
    MONEY_LAUNDERING = "money_laundering"
    RECKLESS_LEVERAGE = "reckless_leverage"


class SafetyGuard:
    """
    Deterministic financial-domain safety guard.
    Runs before any LLM call.
    """

    BLOCK_PATTERNS = {
        SafetyCategory.INSIDER_TRADING: [
            r"non[- ]public information",
            r"inside information",
            r"confidential earnings",
        ],
        SafetyCategory.GUARANTEED_RETURNS: [
            r"guaranteed return",
            r"no risk profit",
            r"100% sure",
        ],
        SafetyCategory.MARKET_MANIPULATION: [
            r"pump and dump",
            r"manipulate price",
            r"artificially inflate",
        ],
        SafetyCategory.MONEY_LAUNDERING: [
            r"hide money",
            r"evade tax",
            r"launder",
        ],
        SafetyCategory.RECKLESS_LEVERAGE: [
            r"max leverage",
            r"all in options",
            r"YOLO trade",
        ],
    }

    EDUCATIONAL_HINTS = [
        r"what is",
        r"explain",
        r"definition of",
        r"how does .* work",
    ]

    def check(self, query: str) -> Dict[str, str]:
        if not query or not query.strip():
            return {
                "decision": SafetyDecision.ALLOW.value,
                "reason": "empty_or_neutral_input",
            }

        normalized = query.lower()

        is_educational = any(
            re.search(pattern, normalized)
            for pattern in self.EDUCATIONAL_HINTS
        )

        for category, patterns in self.BLOCK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized):
                    if is_educational:
                        return {
                            "decision": SafetyDecision.ALLOW.value,
                            "reason": f"educational_{category.value}",
                        }
                    return {
                        "decision": SafetyDecision.BLOCK.value,
                        "reason": category.value,
                    }

        return {
            "decision": SafetyDecision.ALLOW.value,
            "reason": "safe_financial_query",
        }