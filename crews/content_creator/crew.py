# crews/content_creator/crew.py
from typing import List, Dict, Any
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.content_creator.analysis_agent import CCAnalysisAgent
from crews.content_creator.output_agent import CCOutputAgent


class ContentCreatorCrew(BaseCrew):
    def __init__(self):
        self._retrieval = CCRetrievalAgent()
        self._analysis = CCAnalysisAgent()
        self._output = CCOutputAgent()

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        return self._retrieval.retrieve(brief, sources)

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._analysis.analyse(retrieved)

    def generate_artifacts(
        self, analysis: Dict[str, Any], selected_artifacts: List[str]
    ) -> List[Dict[str, Any]]:
        return self._output.generate_artifacts(analysis, selected_artifacts)

    def run(self, brief: ResearchBrief) -> CrewOutput:
        retrieved = self.retrieve(brief, brief.selected_sources)
        notes = []
        if self._retrieval.fallback_used:
            notes.append(
                "Selected sources couldn't be scraped (likely paywalled or JS-rendered). "
                "Fell back to a Tavily web search to find relevant content — results are based on publicly available articles."
            )
        analysis = self.analyse(retrieved)
        artifacts = self.generate_artifacts(analysis, brief.selected_artifacts)
        return CrewOutput(artifacts=artifacts, notes=notes)
