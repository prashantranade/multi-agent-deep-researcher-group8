import json
from unittest.mock import patch, MagicMock

from crews.base_crew import ResearchBrief
from crews.tools.tool_context import ToolRuntime, set_runtime, reset_runtime
from crews.tools import cc_tools


def _brief():
    return ResearchBrief(
        topic="Rajasthan travel",
        persona="content_creator",
        audience="millennials",
        tone="inspirational",
        depth="standard",
        selected_sources=[{"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01"}],
    )


def test_scrape_and_index_sources_indexes_chunks():
    runtime = ToolRuntime(brief=_brief(), db_path="/tmp/test")
    token = set_runtime(runtime)
    try:
        with patch("crews.tools.cc_tools.scrape_selected_sources") as mock_scrape, \
             patch("crews.tools.cc_tools.VectorStore") as mock_vs:
            mock_scrape.return_value = [{
                "url": "https://a.com",
                "content": "eco travel " * 200,
                "title": "A",
                "domain": "a.com",
                "date": "2025-01-01",
            }]
            result = cc_tools.scrape_and_index_sources.invoke({})
    finally:
        reset_runtime(token)
    assert "Indexed" in result
    mock_vs.return_value.add_texts.assert_called_once()


def test_search_research_chunks_populates_runtime():
    runtime = ToolRuntime(brief=_brief(), db_path="/tmp/test")
    token = set_runtime(runtime)
    try:
        with patch("crews.tools.cc_tools.VectorStore") as mock_vs:
            mock_vs.return_value.search.return_value = [{"text": "chunk", "metadata": {}}]
            result = cc_tools.search_research_chunks.invoke({})
            payload = json.loads(result)
    finally:
        reset_runtime(token)
    assert payload["chunk_count"] == 1
    assert len(runtime.retrieved) == 1


def test_analyse_content_strategy_requires_chunks():
    runtime = ToolRuntime(brief=_brief(), db_path="/tmp/test")
    token = set_runtime(runtime)
    try:
        result = cc_tools.analyse_content_strategy.invoke({})
    finally:
        reset_runtime(token)
    assert "Error" in result


def test_generate_content_artifact_delegates_to_output_agent():
    runtime = ToolRuntime(
        brief=_brief(),
        db_path="/tmp/test",
        analysis={"trends": ["eco"], "hooks": ["Discover"]},
    )
    token = set_runtime(runtime)
    try:
        with patch("crews.tools.cc_tools.CCOutputAgent") as mock_output:
            mock_output.return_value.generate_artifacts.return_value = [
                {"type": "captions", "content": "caption text", "citations": []}
            ]
            result = cc_tools.generate_content_artifact.invoke({"artifact_type": "captions"})
            payload = json.loads(result)
    finally:
        reset_runtime(token)
    assert payload["type"] == "captions"
    assert len(runtime.artifacts) == 1
