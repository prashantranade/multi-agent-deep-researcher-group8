# crews/bharat_desha/crew.py
from typing import List, Dict, Any

from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.graph_state import make_initial_state
from crews.graph_invoke import invoke_crew_graph
from crews.bharat_desha.graph import build_bharat_desha_graph
from crews.bharat_desha.trend_agent import run_trend_agent
from crews.bharat_desha.seo_agent import run_seo_agent
from crews.bharat_desha.retrieval_agent import run_retrieval_agent
from crews.bharat_desha.analysis_agent import run_analysis_agent
from crews.bharat_desha.content_agent import run_content_agent
from crews.bharat_desha.social_agent import run_social_agent
from crews.tools.bd_tools import seo_keywords_artifact, _SOCIAL_PLATFORMS, _PRIMARY_CONTENT_TYPES


class BharatDeshaCrew(BaseCrew):
    def __init__(self):
        self._graph = build_bharat_desha_graph()
        self._brief: ResearchBrief | None = None
        self._trend_context: Dict[str, Any] = {}
        self._seo_context: Dict[str, Any] = {}

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        return run_retrieval_agent(brief.topic, self._seo_context)

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        return run_analysis_agent(retrieved, self._seo_context, self._trend_context)

    def generate_artifacts(
        self, analysis: Dict[str, Any], selected_artifacts: List[str]
    ) -> List[Dict[str, Any]]:
        artifacts = [seo_keywords_artifact(self._seo_context)]

        primary_type = next(
            (a for a in selected_artifacts if a in _PRIMARY_CONTENT_TYPES),
            None,
        )
        primary_artifact = None
        if primary_type and self._brief:
            primary_artifact = run_content_agent(
                analysis,
                self._seo_context,
                artifact_type=primary_type,
                tone=self._brief.tone,
                depth=self._brief.depth,
            )
            artifacts.append(primary_artifact)

        selected_platforms = [a for a in selected_artifacts if a in _SOCIAL_PLATFORMS]
        if selected_platforms and primary_artifact:
            artifacts.extend(
                run_social_agent(
                    primary_artifact,
                    analysis.get("key_points", []),
                    self._seo_context,
                    platforms=selected_platforms,
                )
            )

        return artifacts

    def run(
        self,
        brief: ResearchBrief,
        *,
        session_id: str | None = None,
        user_id: str = "anonymous",
    ) -> CrewOutput:
        self._brief = brief
        result, trace_id = invoke_crew_graph(
            self._graph,
            make_initial_state(brief),
            session_id=session_id,
            user_id=user_id,
        )
        self._trend_context = result.get("trend_context") or {}
        self._seo_context = result.get("seo_context") or {}
        return CrewOutput(artifacts=result["artifacts"], trace_id=trace_id)
