from typing import List, Dict, Any

from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.graph_state import make_initial_state
from crews.graph_invoke import invoke_crew_graph
from crews.product_manager.graph import build_product_manager_graph
from crews.product_manager.retrieval_agent import PMRetrievalAgent
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent


class ProductManagerCrew(BaseCrew):
    def __init__(self, db_path: str = ".lancedb_pm"):
        self._retrieval = PMRetrievalAgent(db_path=db_path)
        self._analysis = PMAnalysisAgent()
        self._output = PMOutputAgent()
        self._graph = build_product_manager_graph(db_path=db_path)

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
