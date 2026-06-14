from unittest.mock import patch

from crews.base_crew import ResearchBrief
from crews.bharat_desha.graph import build_bharat_desha_graph
from crews.tools.tool_context import get_runtime
from crews.tools.bd_tools import BD_RETRIEVE_TOOLS, BD_ANALYSE_TOOLS, BD_GENERATE_TOOLS


def _mock_trend():
    return {
        "trends": ["Varanasi trending"],
        "seasonality": {
            "best_months": ["October"],
            "avoid_months": [],
            "active_festivals": [],
            "advisories": [],
        },
        "topic_suggestions": ["Varanasi ghats guide"],
    }


def _mock_seo():
    return {
        "keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}],
        "primary_keyword": "Varanasi spiritual tour",
    }


def _react_side_effect(tools, system_prompt, user_message, **kwargs):
    runtime = get_runtime()
    if list(tools) == BD_RETRIEVE_TOOLS:
        runtime.retrieved = [{"text": "Varanasi is sacred...", "metadata": {"source": "https://example.com"}}]
    elif list(tools) == BD_ANALYSE_TOOLS:
        runtime.analysis = {
            "spiritual": "Sacred city...",
            "practical": "Fly to VNS...",
            "cultural": "Ganga aarti...",
            "wellness": "Ashrams nearby...",
            "seasonal": "Oct-March best...",
            "key_points": ["Visit at dawn"],
            "citations": ["https://example.com"],
        }
    elif list(tools) == BD_GENERATE_TOOLS:
        runtime.primary_artifact = {
            "type": "blog_post",
            "content": "# Varanasi Guide\n\n...",
            "citations": [],
        }
        runtime.artifacts = [
            runtime.primary_artifact,
            {"type": "instagram", "content": "Caption here..."},
        ]


def test_bd_graph_compiles():
    graph = build_bharat_desha_graph()
    assert hasattr(graph, "invoke")


def test_bd_hybrid_graph_full_pipeline():
    brief = ResearchBrief(
        topic="Varanasi spiritual tour",
        persona="bharat_desha",
        audience="solo spiritual travellers",
        tone="warm",
        depth="standard",
        selected_artifacts=["blog_post", "instagram"],
    )
    with patch("crews.bharat_desha.graph.run_trend_agent", return_value=_mock_trend()), \
         patch("crews.bharat_desha.graph.run_seo_agent", return_value=_mock_seo()), \
         patch("crews.bharat_desha.graph.run_react_phase", side_effect=_react_side_effect):
        graph = build_bharat_desha_graph()
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

    artifact_types = [a["type"] for a in result["artifacts"]]
    assert "seo_keywords" in artifact_types
    assert "blog_post" in artifact_types
    assert "instagram" in artifact_types


def test_bd_graph_retries_analysis_on_invalid_json():
    brief = ResearchBrief(
        topic="t", persona="bharat_desha", audience="a", tone="t", depth="standard",
        selected_artifacts=["blog_post"],
    )
    call_count = {"n": 0}

    def analyse_side_effect(tools, system_prompt, user_message, **kwargs):
        runtime = get_runtime()
        if list(tools) == BD_RETRIEVE_TOOLS:
            runtime.retrieved = [{"text": "x", "metadata": {}}]
        elif list(tools) == BD_ANALYSE_TOOLS:
            call_count["n"] += 1
            if call_count["n"] == 1:
                runtime.analysis = {"spiritual": "", "key_points": []}
            else:
                runtime.analysis = {"spiritual": "Sacred", "key_points": ["point"]}
        elif list(tools) == BD_GENERATE_TOOLS:
            runtime.primary_artifact = {"type": "blog_post", "content": "ok", "citations": []}
            runtime.artifacts = [runtime.primary_artifact]

    with patch("crews.bharat_desha.graph.run_trend_agent", return_value=_mock_trend()), \
         patch("crews.bharat_desha.graph.run_seo_agent", return_value=_mock_seo()), \
         patch("crews.bharat_desha.graph.run_react_phase", side_effect=analyse_side_effect):
        graph = build_bharat_desha_graph()
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
    assert any(a["type"] == "blog_post" for a in result["artifacts"])
