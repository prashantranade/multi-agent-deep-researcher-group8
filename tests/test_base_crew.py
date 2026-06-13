# tests/test_base_crew.py
import pytest
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput

def test_base_crew_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        BaseCrew()

def test_concrete_crew_must_implement_all_methods():
    class IncompleteCrew(BaseCrew):
        def retrieve(self, brief, sources):
            return []
        # missing analyse and generate_artifacts

    with pytest.raises(TypeError):
        IncompleteCrew()

def test_concrete_crew_works_when_fully_implemented():
    class MockCrew(BaseCrew):
        def retrieve(self, brief, sources):
            return [{"text": "retrieved", "metadata": {}}]
        def analyse(self, retrieved):
            return {"summary": "analysis done"}
        def generate_artifacts(self, analysis, selected_artifacts):
            return [{"type": "brief", "content": "output", "citations": []}]

    crew = MockCrew()
    brief = ResearchBrief(
        topic="test", persona="content_creator",
        audience="general", tone="neutral", depth="standard"
    )
    result = crew.run(brief)
    assert isinstance(result, CrewOutput)
    assert len(result.artifacts) == 1
    assert result.artifacts[0]["content"] == "output"

def test_research_brief_defaults():
    brief = ResearchBrief(
        topic="test", persona="content_creator",
        audience="general", tone="neutral", depth="standard"
    )
    assert brief.context_text is None
    assert brief.selected_sources == []
    assert brief.selected_artifacts == []

def test_crew_output_trace_id_optional():
    output = CrewOutput(artifacts=[])
    assert output.trace_id is None
    output2 = CrewOutput(artifacts=[], trace_id="abc-123")
    assert output2.trace_id == "abc-123"
