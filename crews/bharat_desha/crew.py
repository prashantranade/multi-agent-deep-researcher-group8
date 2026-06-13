# crews/bharat_desha/crew.py
from typing import List, Dict, Any, TypedDict
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.bharat_desha.trend_agent import run_trend_agent
from crews.bharat_desha.seo_agent import run_seo_agent
from crews.bharat_desha.retrieval_agent import run_retrieval_agent
from crews.bharat_desha.analysis_agent import run_analysis_agent
from crews.bharat_desha.content_agent import run_content_agent
from crews.bharat_desha.social_agent import run_social_agent
from langgraph.graph import StateGraph, START, END

_SOCIAL_PLATFORMS = {"instagram", "facebook", "x_post", "youtube"}
_PRIMARY_CONTENT_TYPES = {"blog_post", "itinerary", "destination_guide", "wellness_guide"}


class BharatDeshaState(TypedDict):
    brief: ResearchBrief
    trend_context: Dict[str, Any]
    seo_context: Dict[str, Any]
    retrieved_chunks: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    artifacts: List[Dict[str, Any]]


class BharatDeshaCrew(BaseCrew):
    def __init__(self):
        # Build LangGraph StateGraph
        builder = StateGraph(BharatDeshaState)

        def trend_node(state: BharatDeshaState) -> Dict[str, Any]:
            trend_context = run_trend_agent(state["brief"].topic)
            return {"trend_context": trend_context}

        def seo_node(state: BharatDeshaState) -> Dict[str, Any]:
            seo_context = run_seo_agent(state["brief"].topic, state["trend_context"])
            return {"seo_context": seo_context}

        def retrieve_node(state: BharatDeshaState) -> Dict[str, Any]:
            self._seo_context = state["seo_context"]
            retrieved = self.retrieve(state["brief"], state["brief"].selected_sources)
            return {"retrieved_chunks": retrieved}

        def analyse_node(state: BharatDeshaState) -> Dict[str, Any]:
            self._seo_context = state["seo_context"]
            self._trend_context = state["trend_context"]
            analysis = self.analyse(state["retrieved_chunks"])
            return {"analysis": analysis}

        def generate_artifacts_node(state: BharatDeshaState) -> Dict[str, Any]:
            self._seo_context = state["seo_context"]
            self._trend_context = state["trend_context"]
            self._brief = state["brief"]
            artifacts = self.generate_artifacts(state["analysis"], state["brief"].selected_artifacts)
            return {"artifacts": artifacts}

        builder.add_node("trend", trend_node)
        builder.add_node("seo", seo_node)
        builder.add_node("retrieve", retrieve_node)
        builder.add_node("analyse", analyse_node)
        builder.add_node("generate_artifacts", generate_artifacts_node)

        builder.add_edge(START, "trend")
        builder.add_edge("trend", "seo")
        builder.add_edge("seo", "retrieve")
        builder.add_edge("retrieve", "analyse")
        builder.add_edge("analyse", "generate_artifacts")
        builder.add_edge("generate_artifacts", END)

        self._graph = builder.compile()

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        return run_retrieval_agent(brief.topic, self._seo_context)

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        return run_analysis_agent(retrieved, self._seo_context, self._trend_context)

    def generate_artifacts(self, analysis: Dict[str, Any], selected_artifacts: List[str]) -> List[Dict[str, Any]]:
        artifacts = []

        # SEO keywords artifact — always included
        keyword_lines = "\n".join(
            f"{i+1}. {k['keyword']} ({k['intent']})"
            for i, k in enumerate(self._seo_context.get("keywords", []))
        )
        artifacts.append({"type": "seo_keywords", "content": keyword_lines, "citations": []})

        # Primary content artifact
        primary_type = next((a for a in selected_artifacts if a in _PRIMARY_CONTENT_TYPES), None)
        primary_artifact = None
        if primary_type:
            primary_artifact = run_content_agent(
                analysis, self._seo_context,
                artifact_type=primary_type,
                tone=self._brief.tone,
                depth=self._brief.depth,
            )
            artifacts.append(primary_artifact)

        # Social repurposing — only for selected platforms
        selected_platforms = [a for a in selected_artifacts if a in _SOCIAL_PLATFORMS]
        if selected_platforms and primary_artifact:
            social_artifacts = run_social_agent(
                primary_artifact,
                analysis.get("key_points", []),
                self._seo_context,
                platforms=selected_platforms,
            )
            artifacts.extend(social_artifacts)

        return artifacts

    def run(self, brief: ResearchBrief) -> CrewOutput:
        initial_state = {
            "brief": brief,
            "trend_context": {},
            "seo_context": {},
            "retrieved_chunks": [],
            "analysis": {},
            "artifacts": [],
        }
        result = self._graph.invoke(initial_state)
        return CrewOutput(artifacts=result["artifacts"])
