from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from typing import List, Dict, Any


class ContentCreatorCrew(BaseCrew):
    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        return []

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {}

    def generate_artifacts(self, analysis: Dict[str, Any], selected_artifacts: List[str]) -> List[Dict[str, Any]]:
        return []
