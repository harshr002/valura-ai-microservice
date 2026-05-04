from src.safety.guard import SafetyGuard, SafetyDecision


class FakeLLM:
    def __init__(self):
        self.called = False

    def classify(self, query, conversation):
        self.called = True
        return {}


def test_safety_precedence():
    safety_guard = SafetyGuard()

    fake_llm = FakeLLM()

    result = safety_guard.check(
        "I have insider information before earnings"
    )

    assert result["decision"] == SafetyDecision.BLOCK.value

    # LLM must never be called
    assert fake_llm.called is False