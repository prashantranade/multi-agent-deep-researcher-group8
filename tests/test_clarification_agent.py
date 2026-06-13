from intake.clarification_agent import ClarificationAgent


def test_get_next_question_returns_audience_first():
    agent = ClarificationAgent()
    result = agent.get_next_question("Rajasthan travel", "content_creator", None, {})
    assert result is not None
    field, question = result
    assert field == "audience"
    assert "audience" in question.lower()


def test_get_next_question_advances_after_audience_answered():
    agent = ClarificationAgent()
    result = agent.get_next_question(
        "Rajasthan travel", "content_creator", None, {"audience": "millennials"}
    )
    field, _ = result
    assert field == "tone"


def test_get_next_question_returns_none_when_complete():
    agent = ClarificationAgent()
    answers = {"audience": "millennials", "tone": "inspirational", "depth": "standard"}
    assert agent.get_next_question("Rajasthan travel", "content_creator", None, answers) is None


def test_build_brief_uses_collected_answers():
    agent = ClarificationAgent()
    brief = agent.build_brief(
        "Rajasthan travel",
        "content_creator",
        "some context",
        {"audience": "millennials", "tone": "inspirational", "depth": "deep"},
    )
    assert brief.audience == "millennials"
    assert brief.tone == "inspirational"
    assert brief.depth == "deep"
    assert brief.context_text == "some context"
