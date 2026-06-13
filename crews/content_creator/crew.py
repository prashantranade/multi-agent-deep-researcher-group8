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
