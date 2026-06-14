import json
from unittest.mock import patch

from crews.base_crew import ResearchBrief
from crews.tools.tool_context import ToolRuntime, set_runtime, reset_runtime
from crews.tools import pm_tools


def _brief():
    return ResearchBrief(
        topic="sustainable travel market India",
        persona="product_manager",
        audience="investors",
        tone="analytical",
        depth="deep",
        selected_sources=[
            {"url": "https://mckinsey.com/a", "title": "M", "domain": "mckinsey.com", "date": "2025-01-01"}
        ],
    )


def test_scrape_and_index_market_sources_indexes_chunks():
    runtime = ToolRuntime(brief=_brief(), db_path="/tmp/test")
    token = set_runtime(runtime)
    try:
        with patch("crews.tools.pm_tools.scrape_selected_sources") as mock_scrape, \
             patch("crews.tools.pm_tools.VectorStore") as mock_vs:
            mock_scrape.return_value = [{
                "url": "https://mckinsey.com/a",
                "content": "market growing 20% YoY " * 50,
                "title": "M",
                "domain": "mckinsey.com",
                "date": "2025-01-01",
            }]
            result = pm_tools.scrape_and_index_market_sources.invoke({})
    finally:
        reset_runtime(token)
    assert "Indexed" in result
    mock_vs.return_value.drop_table.assert_called_once_with("pm_research")
    mock_vs.return_value.add_texts.assert_called_once()


def test_search_market_research_chunks_populates_runtime():
    runtime = ToolRuntime(brief=_brief(), db_path="/tmp/test")
    token = set_runtime(runtime)
    try:
        with patch("crews.tools.pm_tools.VectorStore") as mock_vs:
            mock_vs.return_value.search.return_value = [{"text": "market data", "metadata": {}}]
            result = pm_tools.search_market_research_chunks.invoke({})
            payload = json.loads(result)
    finally:
        reset_runtime(token)
    assert payload["chunk_count"] == 1
    assert len(runtime.retrieved) == 1


def test_analyse_market_strategy_requires_chunks():
    runtime = ToolRuntime(brief=_brief(), db_path="/tmp/test")
    token = set_runtime(runtime)
    try:
        result = pm_tools.analyse_market_strategy.invoke({})
    finally:
        reset_runtime(token)
    assert "Error" in result


def test_generate_pm_artifact_delegates_to_output_agent():
    runtime = ToolRuntime(
        brief=_brief(),
        db_path="/tmp/test",
        analysis={"market_size": "large", "competitors": ["BookMyTrip"]},
    )
    token = set_runtime(runtime)
    try:
        with patch("crews.tools.pm_tools.PMOutputAgent") as mock_output:
            mock_output.return_value.generate_artifacts.return_value = [
                {"type": "research_brief", "content": "brief text", "citations": []}
            ]
            result = pm_tools.generate_pm_artifact.invoke({"artifact_type": "research_brief"})
            payload = json.loads(result)
    finally:
        reset_runtime(token)
    assert payload["type"] == "research_brief"
    assert len(runtime.artifacts) == 1
