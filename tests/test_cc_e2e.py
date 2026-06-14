# tests/test_cc_e2e.py
from unittest.mock import patch

from crews.base_crew import ResearchBrief, CrewOutput
from crews.content_creator.crew import ContentCreatorCrew
from crews.tools.tool_context import get_runtime
from crews.tools.cc_tools import CC_RETRIEVE_TOOLS, CC_ANALYSE_TOOLS, CC_GENERATE_TOOLS


def _react_side_effect(tools, system_prompt, user_message, **kwargs):
    runtime = get_runtime()
    if list(tools) == CC_RETRIEVE_TOOLS:
        runtime.retrieved = [{"text": "eco travel", "metadata": {"source": "a.com"}}]
    elif list(tools) == CC_ANALYSE_TOOLS:
        runtime.analysis = {
            "trends": ["eco tourism"],
            "hooks": ["Discover Rajasthan"],
            "audience_signals": ["millennials"],
            "tone_notes": "inspirational",
            "key_facts": [],
        }
    elif list(tools) == CC_GENERATE_TOOLS:
        artifact_type = runtime.artifact_type or "content_brief"
        runtime.artifacts = [
            {"type": artifact_type, "content": f"{artifact_type} content", "citations": []}
        ]


def test_cc_crew_full_pipeline(tmp_path):
    brief = ResearchBrief(
        topic="sustainable travel Rajasthan",
        persona="content_creator",
        audience="millennials",
        tone="inspirational",
        depth="standard",
        selected_sources=[{"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01"}],
        selected_artifacts=["content_brief", "captions"],
    )
    with patch("crews.content_creator.graph.run_react_phase", side_effect=_react_side_effect):
        crew = ContentCreatorCrew(db_path=str(tmp_path))
        result = crew.run(brief)
        artifacts = result.artifacts

    assert isinstance(result, CrewOutput)
    assert len(artifacts) == 2
    types = [a["type"] for a in artifacts]
    assert "content_brief" in types
    assert "captions" in types


def test_content_creator_crew_run_uses_langgraph():
    from unittest.mock import MagicMock
    from crews.content_creator.crew import ContentCreatorCrew
    from crews.base_crew import CrewOutput

    crew = ContentCreatorCrew()
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "artifacts": [{"type": "content_brief", "content": "x", "citations": []}],
    }
    crew._graph = mock_graph
    brief = ResearchBrief(
        topic="t", persona="content_creator", audience="a", tone="t", depth="standard",
        selected_artifacts=["content_brief"],
    )
    result = crew.run(brief)
    assert isinstance(result, CrewOutput)
    mock_graph.invoke.assert_called_once()
