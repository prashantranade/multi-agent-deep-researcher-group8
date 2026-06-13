# tests/test_cc_output.py
from unittest.mock import patch
from crews.content_creator.output_agent import CCOutputAgent


def test_cc_output_generates_selected_artifacts():
    with patch("crews.content_creator.output_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = "Generated content here"
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
    with patch("crews.content_creator.output_agent.chat_with_fallback") as mock_llm:
        mock_llm.return_value = "Generated"
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
