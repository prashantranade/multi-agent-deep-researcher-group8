# tests/test_cc_retrieval.py
from unittest.mock import patch
from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.base_crew import ResearchBrief


def test_cc_retrieval_returns_list(tmp_path):
    with patch("crews.content_creator.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.content_creator.retrieval_agent.VectorStore") as mock_vs:
        mock_scrape.return_value = [{
            "url": "https://a.com",
            "content": "travel content about Rajasthan",
            "title": "A",
            "domain": "a.com",
            "date": "2025-01-01",
        }]
        mock_vs.return_value.search.return_value = [{
            "text": "travel content",
            "metadata": {"source": "https://a.com"},
        }]
        agent = CCRetrievalAgent(db_path=str(tmp_path))
        brief = ResearchBrief(
            topic="sustainable travel Rajasthan",
            persona="content_creator",
            audience="millennials",
            tone="inspirational",
            depth="standard",
        )
        results = agent.retrieve(
            brief,
            sources=[{"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01"}],
        )
    assert isinstance(results, list)
    assert len(results) > 0


def test_cc_retrieval_prioritises_social_sources():
    agent = CCRetrievalAgent()
    joined = " ".join(agent.PRIORITY_SOURCES).lower()
    assert "instagram" in agent.PRIORITY_SOURCES or "travel" in joined
