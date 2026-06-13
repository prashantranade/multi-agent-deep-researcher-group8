# crews/bharat_desha/crew.py
from typing import List, Dict, Any
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.bharat_desha.trend_agent import run_trend_agent
from crews.bharat_desha.seo_agent import run_seo_agent
from crews.bharat_desha.retrieval_agent import run_retrieval_agent
from crews.bharat_desha.analysis_agent import run_analysis_agent
from crews.bharat_desha.content_agent import run_content_agent
from crews.bharat_desha.social_agent import run_social_agent

_SOCIAL_PLATFORMS = {"instagram", "facebook", "x_post", "youtube"}
_PRIMARY_CONTENT_TYPES = {"blog_post", "itinerary", "destination_guide", "wellness_guide"}

class BharatDeshaCrew(BaseCrew):

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
        self._brief = brief
        self._trend_context = run_trend_agent(brief.topic)
        self._seo_context = run_seo_agent(brief.topic, self._trend_context)

        retrieved = self.retrieve(brief, brief.selected_sources)
        analysis = self.analyse(retrieved)
        artifacts = self.generate_artifacts(analysis, brief.selected_artifacts)
        return CrewOutput(artifacts=artifacts)
