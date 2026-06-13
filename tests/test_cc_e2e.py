# tests/test_cc_e2e.py
from unittest.mock import patch
from crews.base_crew import ResearchBrief, CrewOutput
from crews.content_creator.crew import ContentCreatorCrew


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
         patch("crews.content_creator.analysis_agent.chat_with_fallback") as mock_analysis_llm, \
         patch("crews.content_creator.output_agent.chat_with_fallback") as mock_output_llm:

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
        mock_analysis_llm.return_value = analysis_json
        mock_output_llm.return_value = "Generated content"

        crew = ContentCreatorCrew(db_path=str(tmp_path))
        result = crew.run(brief)
        artifacts = result.artifacts

    assert isinstance(result, CrewOutput)
    assert len(artifacts) == 2
    types = [a["type"] for a in artifacts]
    assert "content_brief" in types
    assert "captions" in types
