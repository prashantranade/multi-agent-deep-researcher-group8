# crews/product_manager/crew.py
from typing import List, Dict, Any, TypedDict
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.product_manager.retrieval_agent import PMRetrievalAgent
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent
from langgraph.graph import StateGraph, START, END


class ProductManagerState(TypedDict):
    brief: ResearchBrief
    retrieved_chunks: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    artifacts: List[Dict[str, Any]]
    notes: List[str]


class ProductManagerCrew(BaseCrew):
    def __init__(self):
        self._retrieval = PMRetrievalAgent()
        self._analysis = PMAnalysisAgent()
        self._output = PMOutputAgent()

        # Build LangGraph
        builder = StateGraph(ProductManagerState)

        def retrieve_node(state: ProductManagerState) -> Dict[str, Any]:
            retrieved = self.retrieve(state["brief"], state["brief"].selected_sources)
            notes = []
            if self._retrieval.fallback_used:
                notes.append(
                    "Selected sources couldn't be scraped (likely paywalled or JS-rendered). "
                    "Fell back to a Tavily web search to find relevant content — results are based on publicly available articles."
                )
            return {"retrieved_chunks": retrieved, "notes": notes}

        def analyse_node(state: ProductManagerState) -> Dict[str, Any]:
            analysis = self.analyse(state["retrieved_chunks"])
            return {"analysis": analysis}

        def generate_artifacts_node(state: ProductManagerState) -> Dict[str, Any]:
            artifacts = self.generate_artifacts(state["analysis"], state["brief"].selected_artifacts)
            return {"artifacts": artifacts}

        builder.add_node("retrieve", retrieve_node)
        builder.add_node("analyse", analyse_node)
        builder.add_node("generate_artifacts", generate_artifacts_node)

        builder.add_edge(START, "retrieve")
        builder.add_edge("retrieve", "analyse")
        builder.add_edge("analyse", "generate_artifacts")
        builder.add_edge("generate_artifacts", END)

        self._graph = builder.compile()

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        return self._retrieval.retrieve(brief, sources)

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._analysis.analyse(retrieved)

    def generate_artifacts(
        self, analysis: Dict[str, Any], selected_artifacts: List[str]
    ) -> List[Dict[str, Any]]:
        return self._output.generate_artifacts(analysis, selected_artifacts)

    def run(self, brief: ResearchBrief) -> CrewOutput:
        initial_state = {
            "brief": brief,
            "retrieved_chunks": [],
            "analysis": {},
            "artifacts": [],
            "notes": [],
        }
        result = self._graph.invoke(initial_state)
        return CrewOutput(artifacts=result["artifacts"], notes=result.get("notes", []))
