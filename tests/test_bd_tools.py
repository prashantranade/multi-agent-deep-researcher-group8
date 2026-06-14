import json
from unittest.mock import patch

from crews.base_crew import ResearchBrief
from crews.tools.tool_context import ToolRuntime, set_runtime, reset_runtime
from crews.tools import bd_tools


def _brief():
    return ResearchBrief(
        topic="Varanasi spiritual tour",
        persona="bharat_desha",
        audience="solo spiritual travellers",
        tone="warm",
        depth="standard",
        selected_artifacts=["blog_post", "instagram"],
    )


def _seo_context():
    return {
        "keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}],
        "primary_keyword": "Varanasi spiritual tour",
    }


def test_search_and_index_travel_research_populates_runtime():
    runtime = ToolRuntime(brief=_brief(), db_path="", seo_context=_seo_context())
    token = set_runtime(runtime)
    try:
        with patch("crews.tools.bd_tools.run_retrieval_agent") as mock_retrieve:
            mock_retrieve.return_value = [{"text": "Varanasi is sacred...", "metadata": {}}]
            result = bd_tools.search_and_index_travel_research.invoke({})
            payload = json.loads(result)
    finally:
        reset_runtime(token)
    assert payload["chunk_count"] == 1
    assert len(runtime.retrieved) == 1


def test_analyse_bharat_desha_research_requires_chunks():
    runtime = ToolRuntime(brief=_brief(), db_path="", seo_context=_seo_context())
    token = set_runtime(runtime)
    try:
        result = bd_tools.analyse_bharat_desha_research.invoke({})
    finally:
        reset_runtime(token)
    assert "Error" in result


def test_generate_primary_travel_content_delegates():
    runtime = ToolRuntime(
        brief=_brief(),
        db_path="",
        seo_context=_seo_context(),
        analysis={"spiritual": "Sacred", "key_points": ["Visit at dawn"]},
    )
    token = set_runtime(runtime)
    try:
        with patch("crews.tools.bd_tools.run_content_agent") as mock_content:
            mock_content.return_value = {
                "type": "blog_post",
                "content": "# Varanasi Guide",
                "citations": [],
            }
            result = bd_tools.generate_primary_travel_content.invoke({"artifact_type": "blog_post"})
            payload = json.loads(result)
    finally:
        reset_runtime(token)
    assert payload["type"] == "blog_post"
    assert runtime.primary_artifact is not None


def test_generate_social_travel_content_requires_primary():
    runtime = ToolRuntime(
        brief=_brief(),
        db_path="",
        seo_context=_seo_context(),
        analysis={"key_points": ["Visit at dawn"]},
    )
    token = set_runtime(runtime)
    try:
        result = bd_tools.generate_social_travel_content.invoke({"platform": "instagram"})
    finally:
        reset_runtime(token)
    assert "Error" in result


def test_seo_keywords_artifact_formats_keywords():
    artifact = bd_tools.seo_keywords_artifact(_seo_context())
    assert artifact["type"] == "seo_keywords"
    assert "Varanasi spiritual tour" in artifact["content"]
