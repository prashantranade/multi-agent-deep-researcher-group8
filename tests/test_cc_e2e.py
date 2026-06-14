# tests/test_cc_e2e.py
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from crews.base_crew import ResearchBrief
from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.content_creator.analysis_agent import CCAnalysisAgent
from crews.content_creator.output_agent import CCOutputAgent


def test_cc_crew_full_pipeline(tmp_path):
    brief = ResearchBrief(
        topic="sustainable travel Rajasthan",
        persona="content_creator",
        audience="millennials",
        tone="inspirational",
        depth="standard",
        selected_sources=[{"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01"}],
        selected_artifacts=["content_brief", "captions"],
    )
    analysis_json = (
        '{"trends": ["eco tourism"], "hooks": ["Discover Rajasthan"], '
        '"audience_signals": ["millennials"], "tone_notes": "inspirational", "key_facts": []}'
    )
    with patch("crews.content_creator.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.content_creator.retrieval_agent.VectorStore") as mock_vs, \
         patch("crews.content_creator.analysis_agent.get_llm") as mock_analysis_get_llm, \
         patch("crews.content_creator.output_agent.get_llm") as mock_output_get_llm:

        mock_scrape.return_value = [{
            "url": "https://a.com",
            "content": "Rajasthan eco travel",
            "title": "A",
            "domain": "a.com",
            "date": "2025-01-01",
        }]
        mock_vs.return_value.search.return_value = [{
            "text": "eco travel content",
            "metadata": {"source": "a.com"},
        }]

        mock_analysis_llm = MagicMock()
        mock_analysis_llm.invoke.return_value = AIMessage(content=analysis_json)
        mock_analysis_get_llm.return_value = mock_analysis_llm

        mock_output_llm = MagicMock()
        mock_output_llm.invoke.return_value = AIMessage(content="Generated content")
        mock_output_get_llm.return_value = mock_output_llm

        retrieval = CCRetrievalAgent(db_path=str(tmp_path))
        analysis = CCAnalysisAgent()
        output = CCOutputAgent()

        retrieved = retrieval.retrieve(brief, brief.selected_sources)
        analysed = analysis.analyse(retrieved)
        artifacts = output.generate_artifacts(analysed, brief.selected_artifacts)

    assert len(artifacts) == 2
    types = [a["type"] for a in artifacts]
    assert "content_brief" in types
    assert "captions" in types

