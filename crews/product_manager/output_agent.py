# crews/product_manager/output_agent.py
import json
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from infrastructure.llm_client import get_llm
from outputs.product_manager.templates import (
    RESEARCH_BRIEF_PROMPT,
    COMPETITIVE_SUMMARY_PROMPT,
    OPPORTUNITY_SIZING_PROMPT,
    PRD_INSIGHTS_PROMPT,
)
import config


class PMOutputAgent:
    def __init__(self):
        self.model = config.OUTPUT_MODEL

    def _generate(self, prompt: str) -> str:
        llm = get_llm(self.model)
        response = llm.invoke([HumanMessage(content=prompt)])
        return str(response.content)

    def generate_artifacts(
        self, analysis: Dict[str, Any], selected_artifacts: List[str]
    ) -> List[Dict[str, Any]]:
        analysis_text = json.dumps(analysis, indent=2)
        generators = {
            "research_brief": lambda: self._generate(
                RESEARCH_BRIEF_PROMPT.format(analysis=analysis_text)
            ),
            "competitive_summary": lambda: self._generate(
                COMPETITIVE_SUMMARY_PROMPT.format(analysis=analysis_text)
            ),
            "opportunity_sizing": lambda: self._generate(
                OPPORTUNITY_SIZING_PROMPT.format(analysis=analysis_text)
            ),
            "prd_insights": lambda: self._generate(
                PRD_INSIGHTS_PROMPT.format(analysis=analysis_text)
            ),
        }
        artifacts = []
        for artifact_type in selected_artifacts:
            if artifact_type in generators:
                artifacts.append({
                    "type": artifact_type,
                    "content": generators[artifact_type](),
                    "citations": [],
                })
        return artifacts
