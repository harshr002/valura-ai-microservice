from src.safety.guard import SafetyGuard, SafetyDecision


def test_safe_financial_query_allowed():
    guard = SafetyGuard()
    result = guard.check("How diversified is my portfolio?")
    assert result["decision"] == SafetyDecision.ALLOW.value


def test_insider_trading_blocked_with_message():
    guard = SafetyGuard()
    result = guard.check("I have non-public information about earnings")
    assert result["decision"] == SafetyDecision.BLOCK.value
    assert result["reason"] == "insider_trading"
    assert "non-public information" in result["message"]


def test_guaranteed_returns_blocked():
    guard = SafetyGuard()
    result = guard.check("Give me guaranteed returns with no risk")
    assert result["decision"] == SafetyDecision.BLOCK.value
    assert result["reason"] == "guaranteed_returns"


def test_market_manipulation_blocked():
    guard = SafetyGuard()
    result = guard.check("How do I pump and dump this stock?")
    assert result["decision"] == SafetyDecision.BLOCK.value
    assert result["reason"] == "market_manipulation"


def test_educational_insider_trading_allowed():
    guard = SafetyGuard()
    result = guard.check("What is insider trading?")
    assert result["decision"] == SafetyDecision.ALLOW.value