from src.safety.guard import SafetyGuard, SafetyDecision


def test_safe_financial_query_allowed():
    guard = SafetyGuard()
    result = guard.check("How diversified is my portfolio?")
    assert result["decision"] == SafetyDecision.ALLOW.value


def test_insider_trading_blocked():
    guard = SafetyGuard()
    result = guard.check("I have non-public information about earnings")
    assert result["decision"] == SafetyDecision.BLOCK.value
    assert result["reason"] == "insider_trading"


def test_educational_insider_trading_allowed():
    guard = SafetyGuard()
    result = guard.check("What is insider trading?")
    assert result["decision"] == SafetyDecision.ALLOW.value