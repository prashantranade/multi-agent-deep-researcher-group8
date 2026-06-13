# tests/test_pm_retrieval.py
from unittest.mock import patch
from crews.product_manager.retrieval_agent import PMRetrievalAgent, _TABLE_NAME
from crews.base_crew import ResearchBrief


def test_pm_retrieval_returns_list(tmp_path):
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs:
        mock_scrape.return_value = [
            {
                "url": "https://mckinsey.com/a",
                "content": "travel market growing 20% YoY",
                "title": "M",
                "domain": "mckinsey.com",
                "date": "2025-01-01",
            }
        ]
        mock_vs.return_value.search.return_value = [
            {"text": "market data", "metadata": {"source": "mckinsey.com"}}
        ]
        agent = PMRetrievalAgent(db_path=str(tmp_path))
        brief = ResearchBrief(
            topic="sustainable travel market India",
            persona="product_manager",
            audience="investors",
            tone="analytical",
            depth="deep",
        )
        results = agent.retrieve(
            brief,
            sources=[{"url": "https://mckinsey.com/a", "title": "M", "domain": "mckinsey.com", "date": "2025-01-01"}],
        )
    assert isinstance(results, list)


def test_pm_retrieval_priority_sources_defined(tmp_path):
    with patch("crews.product_manager.retrieval_agent.VectorStore"):
        agent = PMRetrievalAgent(db_path=str(tmp_path))
    assert "mckinsey.com" in agent.PRIORITY_SOURCES
    assert "hbr.org" in agent.PRIORITY_SOURCES


def test_pm_retrieval_stores_context_text(tmp_path):
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs:
        mock_scrape.return_value = []
        mock_vs.return_value.search.return_value = []
        agent = PMRetrievalAgent(db_path=str(tmp_path))
        brief = ResearchBrief(
            topic="travel market",
            persona="product_manager",
            audience="investors",
            tone="analytical",
            depth="standard",
            context_text="BharatDesha is a travel platform targeting India.",
        )
        agent.retrieve(brief, sources=[])
        mock_vs.return_value.drop_table.assert_called_once_with(_TABLE_NAME)
        mock_vs.return_value.add_texts.assert_called_once()
        texts_passed = mock_vs.return_value.add_texts.call_args[0][0]
        assert mock_vs.return_value.add_texts.call_args[1]["table_name"] == _TABLE_NAME
        assert any("BharatDesha" in t for t in texts_passed)


def test_pm_retrieval_clears_table_before_add(tmp_path):
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs:
        mock_scrape.return_value = [
            {"url": "https://a.com", "content": "data", "title": "A", "domain": "a.com", "date": "2025-01-01"}
        ]
        mock_vs.return_value.search.return_value = []
        agent = PMRetrievalAgent(db_path=str(tmp_path))
        brief = ResearchBrief(
            topic="travel market", persona="product_manager", audience="investors",
            tone="analytical", depth="standard",
        )
        agent.retrieve(brief, sources=[{"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01"}])
        mock_vs.return_value.drop_table.assert_called_once_with(_TABLE_NAME)


def test_pm_retrieval_query_string(tmp_path):
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs, \
         patch("crews.product_manager.retrieval_agent.TavilyClient") as mock_tavily:
        mock_scrape.return_value = []
        mock_vs.return_value.search.return_value = []
        mock_tavily.return_value.search.return_value = {"results": []}
        agent = PMRetrievalAgent(db_path=str(tmp_path))
        brief = ResearchBrief(
            topic="edtech India", persona="product_manager", audience="founders",
            tone="analytical", depth="deep",
        )
        agent.retrieve(brief, sources=[])
        mock_vs.return_value.search.assert_called_once_with(
            "edtech India market size competition user pain points data",
            table_name=_TABLE_NAME,
            k=10,
        )


def test_pm_retrieval_chunks_limited_to_five(tmp_path):
    long_content = "x" * 6000
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs:
        mock_scrape.return_value = [
            {"url": "https://a.com", "content": long_content, "title": "A", "domain": "a.com", "date": "2025-01-01"}
        ]
        mock_vs.return_value.search.return_value = []
        agent = PMRetrievalAgent(db_path=str(tmp_path))
        brief = ResearchBrief(
            topic="travel market", persona="product_manager", audience="investors",
            tone="analytical", depth="standard",
        )
        agent.retrieve(brief, sources=[{"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01"}])
        texts_passed = mock_vs.return_value.add_texts.call_args[0][0]
        assert len(texts_passed) == 5
