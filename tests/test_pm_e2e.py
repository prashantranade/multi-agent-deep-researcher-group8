# tests/test_pm_e2e.py
from unittest.mock import patch, MagicMock

from crews.base_crew import ResearchBrief, CrewOutput
from crews.product_manager.crew import ProductManagerCrew
from crews.tools.tool_context import get_runtime
from crews.tools.pm_tools import PM_RETRIEVE_TOOLS, PM_ANALYSE_TOOLS, PM_GENERATE_TOOLS


def _react_side_effect(tools, system_prompt, user_message, **kwargs):
    runtime = get_runtime()
    if list(tools) == PM_RETRIEVE_TOOLS:
        runtime.retrieved = [{"text": "market data", "metadata": {"source": "mckinsey.com"}}]
    elif list(tools) == PM_ANALYSE_TOOLS:
        runtime.analysis = {
            "market_size": "large",
            "competitors": ["BookMyTrip"],
            "user_pain_points": ["cost", "trust"],
            "opportunity": "high",
            "contradictions": [],
            "key_data_points": ["20% YoY growth"],
        }
    elif list(tools) == PM_GENERATE_TOOLS:
        artifact_type = runtime.artifact_type or "research_brief"
        runtime.artifacts = [
            {"type": artifact_type, "content": "Generated PM content", "citations": []}
        ]


def test_pm_crew_full_pipeline(tmp_path):
    brief = ResearchBrief(
        topic="sustainable travel market India",
        persona="product_manager",
        audience="investors",
        tone="analytical",
        depth="deep",
        selected_sources=[
            {"url": "https://mckinsey.com/a", "title": "M", "domain": "mckinsey.com", "date": "2025-01-01"}
        ],
        selected_artifacts=["research_brief", "competitive_summary"],
    )
    with patch("crews.product_manager.graph.run_react_phase", side_effect=_react_side_effect):
        crew = ProductManagerCrew(db_path=str(tmp_path))
        result = crew.run(brief)
        artifacts = result.artifacts

    assert isinstance(result, CrewOutput)
    assert len(artifacts) == 2
    types = [a["type"] for a in artifacts]
    assert "research_brief" in types
    assert "competitive_summary" in types
    for artifact in artifacts:
        assert artifact["content"] == "Generated PM content"
        assert artifact["citations"] == []


def test_pm_crew_single_artifact(tmp_path):
    brief = ResearchBrief(
        topic="edtech market India",
        persona="product_manager",
        audience="founders",
        tone="strategic",
        depth="standard",
        selected_sources=[],
        selected_artifacts=["prd_insights"],
    )

    def single_artifact_side_effect(tools, system_prompt, user_message, **kwargs):
        runtime = get_runtime()
        if list(tools) == PM_RETRIEVE_TOOLS:
            runtime.retrieved = []
        elif list(tools) == PM_ANALYSE_TOOLS:
            runtime.analysis = {
                "market_size": "medium",
                "competitors": [],
                "user_pain_points": ["affordability"],
                "opportunity": "underserved rural segment",
                "contradictions": [],
                "key_data_points": [],
            }
        elif list(tools) == PM_GENERATE_TOOLS:
            runtime.artifacts = [{
                "type": "prd_insights",
                "content": "## User Problems\n- Problem: affordability",
                "citations": [],
            }]

    with patch(
        "crews.product_manager.graph.run_react_phase",
        side_effect=single_artifact_side_effect,
    ):
        crew = ProductManagerCrew(db_path=str(tmp_path))
        result = crew.run(brief)
        artifacts = result.artifacts

    assert isinstance(result, CrewOutput)
    assert len(artifacts) == 1
    assert artifacts[0]["type"] == "prd_insights"
    assert "affordability" in artifacts[0]["content"]


def test_product_manager_crew_run_uses_langgraph():
    crew = ProductManagerCrew()
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {
        "artifacts": [{"type": "research_brief", "content": "x", "citations": []}],
    }
    crew._graph = mock_graph
    brief = ResearchBrief(
        topic="t", persona="product_manager", audience="a", tone="t", depth="standard",
        selected_artifacts=["research_brief"],
    )
    result = crew.run(brief)
    assert isinstance(result, CrewOutput)
    mock_graph.invoke.assert_called_once()
