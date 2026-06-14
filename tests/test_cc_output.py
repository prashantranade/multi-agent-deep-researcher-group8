# tests/test_cc_output.py
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from crews.content_creator.output_agent import CCOutputAgent


def test_cc_output_generates_selected_artifacts():
    with patch("crews.content_creator.output_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Generated content here")
        mock_get_llm.return_value = mock_llm
        agent = CCOutputAgent()
        analysis = {
            "trends": ["eco travel"],
            "hooks": ["Hidden Rajasthan"],
            "audience_signals": ["millennials"],
            "tone_notes": "inspirational",
            "key_facts": [],
        }
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["content_brief"])
    assert len(artifacts) == 1
    assert artifacts[0]["type"] == "content_brief"
    assert "content" in artifacts[0]


def test_cc_output_only_generates_selected():
    with patch("crews.content_creator.output_agent.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="Generated")
        mock_get_llm.return_value = mock_llm
        agent = CCOutputAgent()
        analysis = {
            "trends": [],
            "hooks": [],
            "audience_signals": [],
            "tone_notes": "",
            "key_facts": [],
        }
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["captions"])
    types = [a["type"] for a in artifacts]
    assert "captions" in types
    assert "content_brief" not in types

