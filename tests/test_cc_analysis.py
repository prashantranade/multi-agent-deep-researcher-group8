# tests/test_cc_analysis.py
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from crews.content_creator.analysis_agent import CCAnalysisAgent


def test_cc_analysis_returns_dict():
    analysis_json = (
        '{"trends": ["eco tourism"], "hooks": ["Discover hidden Rajasthan"], '
        '"audience_signals": ["millennials prefer authentic"], "tone_notes": "inspirational", '
        '"key_facts": []}'
    )
    with patch("crews.content_creator.analysis_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=analysis_json)
        mock_get_llm.return_value = mock_llm
        agent = CCAnalysisAgent()
        retrieved = [{
            "text": "Rajasthan eco tourism is growing among millennials",
            "metadata": {"source": "https://a.com"},
        }]
        result = agent.analyse(retrieved)
    assert "trends" in result
    assert "hooks" in result
    assert isinstance(result["hooks"], list)

