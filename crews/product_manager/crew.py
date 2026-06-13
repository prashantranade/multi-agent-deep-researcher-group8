# crews/product_manager/crew.py
from typing import List, Dict, Any
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.product_manager.retrieval_agent import PMRetrievalAgent
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent


class ProductManagerCrew(BaseCrew):
    def __init__(self):
        self._retrieval = PMRetrievalAgent()
        self._analysis = PMAnalysisAgent()
        self._output = PMOutputAgent()

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
