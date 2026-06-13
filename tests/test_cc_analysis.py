# tests/test_cc_analysis.py
from unittest.mock import patch
from crews.content_creator.analysis_agent import CCAnalysisAgent


def test_cc_analysis_returns_dict():
    analysis_json = (
        '{"trends": ["eco tourism"], "hooks": ["Discover hidden Rajasthan"], '
        '"audience_signals": ["millennials prefer authentic"], "tone_notes": "inspirational", '
        '"key_facts": []}'
    )
    with patch("crews.content_creator.analysis_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = analysis_json
        agent = CCAnalysisAgent()
        retrieved = [{
            "text": "Rajasthan eco tourism is growing among millennials",
            "metadata": {"source": "https://a.com"},
        }]
        result = agent.analyse(retrieved)
    assert "trends" in result
    assert "hooks" in result
    assert isinstance(result["hooks"], list)
