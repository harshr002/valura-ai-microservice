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


BLOCK_MESSAGES = {
    SafetyCategory.INSIDER_TRADING: (
        "I can’t help with insider trading or using non-public information. "
        "I can explain how insider-trading rules work or discuss investing using public information."
    ),
    SafetyCategory.GUARANTEED_RETURNS: (
        "I can’t promise or help construct guaranteed-return claims. "
        "All investments carry risk, but I can help compare realistic risk and return tradeoffs."
    ),
    SafetyCategory.MARKET_MANIPULATION: (
        "I can’t assist with market manipulation, coordinated pumping, spoofing, or misleading investors. "
        "I can explain legal market mechanics or risk-aware trading concepts."
    ),
    SafetyCategory.MONEY_LAUNDERING: (
        "I can’t help hide, disguise, launder, or illegally move money. "
        "I can discuss legitimate financial compliance and lawful account structuring."
    ),
    SafetyCategory.RECKLESS_LEVERAGE: (
        "I can’t help with reckless all-in or extreme leverage instructions. "
        "I can explain leverage risks and safer position-sizing principles."
    ),
}


class SafetyGuard:
    """
    Deterministic financial safety guard.
    Runs before any LLM/network call.
    """

    BLOCK_PATTERNS = {
        SafetyCategory.INSIDER_TRADING: [
            r"\binsider\s+(info|information|tip)\b",
            r"\bnon[- ]public\s+(info|information)\b",
            r"\bconfidential\s+(earnings|results|announcement)\b",
            r"\bbefore\s+(earnings|announcement|merger)\b.*\b(secret|confidential|leaked)\b",
        ],
        SafetyCategory.GUARANTEED_RETURNS: [
            r"\bguaranteed\s+(return|profit|income)s?\b",
            r"\brisk[- ]free\s+(profit|return)\b",
            r"\bno\s+risk\b.*\bprofit|return\b",
            r"\b100%\s+(sure|safe|guaranteed)\b",
        ],
        SafetyCategory.MARKET_MANIPULATION: [
            r"\bpump\s+and\s+dump\b",
            r"\bmanipulate\s+(a\s+)?(stock|price|market)\b",
            r"\bartificially\s+inflate\b",
            r"\bspoof(ing)?\b",
            r"\bwash\s+trade\b",
            r"\bfake\s+orders?\b",
        ],
        SafetyCategory.MONEY_LAUNDERING: [
            r"\blaunder(ing)?\b",
            r"\bhide\s+(money|funds|cash)\b",
            r"\bclean\s+(dirty\s+)?money\b",
            r"\bevade\s+tax(es)?\b",
            r"\bshell\s+compan(y|ies)\b.*\bhide\b",
        ],
        SafetyCategory.RECKLESS_LEVERAGE: [
            r"\bmax\s+leverage\b",
            r"\b100x\b",
            r"\ball[- ]in\b.*\b(options|crypto|leverage|margin)\b",
            r"\byolo\s+trade\b",
            r"\bbet\s+everything\b",
        ],
    }

    EDUCATIONAL_HINTS = [
        r"\bwhat\s+is\b",
        r"\bexplain\b",
        r"\bdefinition\s+of\b",
        r"\bhow\s+does\b.*\bwork\b",
        r"\bwhy\s+is\b",
        r"\blearn\b",
    ]

    def check(self, query: str) -> Dict[str, str]:
        if not query or not query.strip():
            return {
                "decision": SafetyDecision.ALLOW.value,
                "reason": "empty_or_neutral_input",
                "message": "",
            }

        normalized = query.lower().strip()

        is_educational = any(
            re.search(pattern, normalized) for pattern in self.EDUCATIONAL_HINTS
        )

        for category, patterns in self.BLOCK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized):
                    if is_educational:
                        return {
                            "decision": SafetyDecision.ALLOW.value,
                            "reason": f"educational_{category.value}",
                            "message": "",
                        }

                    return {
                        "decision": SafetyDecision.BLOCK.value,
                        "reason": category.value,
                        "message": BLOCK_MESSAGES[category],
                    }

        return {
            "decision": SafetyDecision.ALLOW.value,
            "reason": "safe_financial_query",
            "message": "",
        }