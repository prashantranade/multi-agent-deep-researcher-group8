from unittest.mock import patch

from crews.base_crew import ResearchBrief
from crews.product_manager.graph import build_product_manager_graph
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
            "user_pain_points": ["cost"],
            "opportunity": "high",
            "contradictions": [],
            "key_data_points": ["20% YoY growth"],
        }
    elif list(tools) == PM_GENERATE_TOOLS:
        artifact_type = runtime.artifact_type or "research_brief"
        runtime.artifacts = [
            {"type": artifact_type, "content": f"{artifact_type} content", "citations": []}
        ]


def test_pm_graph_compiles():
    graph = build_product_manager_graph()
    assert hasattr(graph, "invoke")


def test_pm_hybrid_graph_full_pipeline():
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
        graph = build_product_manager_graph()
        result = graph.invoke({
            "brief": brief,
            "retrieved": [],
            "analysis": {},
            "artifacts": [],
            "errors": [],
            "retry_count": 0,
            "trend_context": None,
            "seo_context": None,
        })
    assert len(result["artifacts"]) == 2
    assert {a["type"] for a in result["artifacts"]} == {"research_brief", "competitive_summary"}


def test_pm_graph_retries_analysis_on_invalid_json():
    brief = ResearchBrief(
        topic="t", persona="product_manager", audience="a", tone="t", depth="standard",
        selected_sources=[], selected_artifacts=["research_brief"],
    )
    call_count = {"n": 0}

    def analyse_side_effect(tools, system_prompt, user_message, **kwargs):
        runtime = get_runtime()
        if list(tools) == PM_RETRIEVE_TOOLS:
            runtime.retrieved = [{"text": "x", "metadata": {}}]
        elif list(tools) == PM_ANALYSE_TOOLS:
            call_count["n"] += 1
            if call_count["n"] == 1:
                runtime.analysis = {"market_size": "unknown", "competitors": []}
            else:
                runtime.analysis = {"market_size": "large", "competitors": ["Acme"]}
        elif list(tools) == PM_GENERATE_TOOLS:
            runtime.artifacts = [{"type": "research_brief", "content": "ok", "citations": []}]

    with patch("crews.product_manager.graph.run_react_phase", side_effect=analyse_side_effect):
        graph = build_product_manager_graph()
        result = graph.invoke({
            "brief": brief,
            "retrieved": [],
            "analysis": {},
            "artifacts": [],
            "errors": [],
            "retry_count": 0,
            "trend_context": None,
            "seo_context": None,
        })
    assert call_count["n"] == 2
    assert len(result["artifacts"]) == 1
