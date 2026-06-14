from unittest.mock import patch

from crews.base_crew import ResearchBrief
from crews.content_creator.graph import build_content_creator_graph
from crews.tools.tool_context import get_runtime
from crews.tools.cc_tools import (
    CC_RETRIEVE_TOOLS,
    CC_ANALYSE_TOOLS,
    CC_GENERATE_TOOLS,
)


def _react_side_effect(tools, system_prompt, user_message, **kwargs):
    runtime = get_runtime()
    if list(tools) == CC_RETRIEVE_TOOLS:
        runtime.retrieved = [{"text": "eco travel", "metadata": {"source": "a.com"}}]
    elif list(tools) == CC_ANALYSE_TOOLS:
        runtime.analysis = {
            "trends": ["eco tourism"],
            "hooks": ["Discover Rajasthan"],
            "audience_signals": [],
            "tone_notes": "inspirational",
            "key_facts": [],
        }
    elif list(tools) == CC_GENERATE_TOOLS:
        artifact_type = runtime.artifact_type or "content_brief"
        runtime.artifacts = [
            {"type": artifact_type, "content": f"{artifact_type} content", "citations": []}
        ]


def test_cc_graph_compiles():
    graph = build_content_creator_graph()
    assert hasattr(graph, "invoke")


def test_cc_hybrid_graph_full_pipeline():
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
        graph = build_content_creator_graph()
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
    assert {a["type"] for a in result["artifacts"]} == {"content_brief", "captions"}


def test_cc_graph_retries_analysis_on_invalid_json():
    brief = ResearchBrief(
        topic="t", persona="content_creator", audience="a", tone="t", depth="standard",
        selected_sources=[], selected_artifacts=["content_brief"],
    )
    call_count = {"n": 0}

    def analyse_side_effect(tools, system_prompt, user_message, **kwargs):
        runtime = get_runtime()
        if list(tools) == CC_RETRIEVE_TOOLS:
            runtime.retrieved = [{"text": "x", "metadata": {}}]
        elif list(tools) == CC_ANALYSE_TOOLS:
            call_count["n"] += 1
            if call_count["n"] == 1:
                runtime.analysis = {"trends": [], "hooks": []}
            else:
                runtime.analysis = {"trends": ["eco"], "hooks": ["hook"]}
        elif list(tools) == CC_GENERATE_TOOLS:
            runtime.artifacts = [{"type": "content_brief", "content": "ok", "citations": []}]

    with patch("crews.content_creator.graph.run_react_phase", side_effect=analyse_side_effect):
        graph = build_content_creator_graph()
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
