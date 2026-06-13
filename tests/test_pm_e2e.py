# tests/test_pm_e2e.py
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from crews.base_crew import ResearchBrief
from crews.product_manager.retrieval_agent import PMRetrievalAgent
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent


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
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs, \
         patch("crews.product_manager.analysis_agent.get_llm") as mock_analysis_get_llm, \
         patch("crews.product_manager.output_agent.get_llm") as mock_output_get_llm:

        mock_scrape.return_value = [
            {"url": "https://mckinsey.com/a", "content": "market growing 20% YoY", "title": "M", "domain": "mckinsey.com", "date": "2025-01-01"}
        ]
        mock_vs.return_value.search.return_value = [
            {"text": "market data", "metadata": {"source": "mckinsey.com"}}
        ]

        mock_analysis_llm = MagicMock()
        mock_analysis_llm.invoke.return_value = AIMessage(content='{"market_size": "large", "competitors": ["BookMyTrip"], "user_pain_points": ["cost", "trust"], "opportunity": "high", "contradictions": [], "key_data_points": ["20% YoY growth"]}')
        mock_analysis_get_llm.return_value = mock_analysis_llm

        mock_output_llm = MagicMock()
        mock_output_llm.invoke.return_value = AIMessage(content="Generated PM content")
        mock_output_get_llm.return_value = mock_output_llm

        retrieval = PMRetrievalAgent(db_path=str(tmp_path))
        analysis = PMAnalysisAgent()
        output = PMOutputAgent()

        retrieved = retrieval.retrieve(brief, brief.selected_sources)
        analysed = analysis.analyse(retrieved)
        artifacts = output.generate_artifacts(analysed, brief.selected_artifacts)

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
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs, \
         patch("crews.product_manager.retrieval_agent.TavilyClient") as mock_tavily, \
         patch("crews.product_manager.analysis_agent.get_llm") as mock_analysis_get_llm, \
         patch("crews.product_manager.output_agent.get_llm") as mock_output_get_llm:

        mock_scrape.return_value = []
        mock_vs.return_value.search.return_value = []
        mock_tavily.return_value.search.return_value = {"results": []}

        mock_analysis_llm = MagicMock()
        mock_analysis_llm.invoke.return_value = AIMessage(content='{"market_size": "medium", "competitors": [], "user_pain_points": ["affordability"], "opportunity": "underserved rural segment", "contradictions": [], "key_data_points": []}')
        mock_analysis_get_llm.return_value = mock_analysis_llm

        mock_output_llm = MagicMock()
        mock_output_llm.invoke.return_value = AIMessage(content="## User Problems\n- Problem: affordability")
        mock_output_get_llm.return_value = mock_output_llm

        retrieved = PMRetrievalAgent(db_path=str(tmp_path)).retrieve(brief, brief.selected_sources)
        analysed = PMAnalysisAgent().analyse(retrieved)
        artifacts = PMOutputAgent().generate_artifacts(analysed, brief.selected_artifacts)

    assert len(artifacts) == 1
    assert artifacts[0]["type"] == "prd_insights"
    assert "affordability" in artifacts[0]["content"]

