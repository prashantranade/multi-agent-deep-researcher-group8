from typing import List, Dict, Any

from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.graph_state import make_initial_state
from crews.graph_invoke import invoke_crew_graph
from crews.content_creator.graph import build_content_creator_graph
from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.content_creator.analysis_agent import CCAnalysisAgent
from crews.content_creator.output_agent import CCOutputAgent


class ContentCreatorCrew(BaseCrew):
    def __init__(self, db_path: str = ".lancedb_cc"):
        self._retrieval = CCRetrievalAgent(db_path=db_path)
        self._analysis = CCAnalysisAgent()
        self._output = CCOutputAgent()
        self._graph = build_content_creator_graph(db_path=db_path)

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        return self._retrieval.retrieve(brief, sources)

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._analysis.analyse(retrieved)

    def generate_artifacts(
        self, analysis: Dict[str, Any], selected_artifacts: List[str]
    ) -> List[Dict[str, Any]]:
        return self._output.generate_artifacts(analysis, selected_artifacts)

    def run(
        self,
        brief: ResearchBrief,
        *,
        session_id: str | None = None,
        user_id: str = "anonymous",
    ) -> CrewOutput:
        result, trace_id = invoke_crew_graph(
            self._graph,
            make_initial_state(brief),
            session_id=session_id,
            user_id=user_id,
        )
        return CrewOutput(artifacts=result["artifacts"], trace_id=trace_id)
