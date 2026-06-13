# crews/product_manager/analysis_agent.py
import json
import re
from typing import List, Dict, Any
from infrastructure.llm_client import chat_with_fallback
import config


def _parse_json_response(raw: str) -> Dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text)


_SYSTEM = """You are a market research analyst. Given research excerpts, identify:
1. Market size and growth signals
2. Key competitors and their positioning
3. User pain points supported by evidence
4. Opportunity areas and gaps
5. Any contradictions or conflicting data across sources

Return valid JSON only with keys: market_size, competitors, user_pain_points, opportunity, contradictions, key_data_points"""


class PMAnalysisAgent:
    def __init__(self):
        self.model = config.ANALYSIS_MODEL

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        context = "\n\n".join(r["text"] for r in retrieved[:8])
        messages = [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Research excerpts:\n{context}\n\nAnalyse for product strategy:"},
        ]
        raw = chat_with_fallback(messages=messages, model=self.model)
        try:
            return _parse_json_response(raw)
        except (json.JSONDecodeError, ValueError):
            return {
                "market_size": "unknown",
                "competitors": [],
                "user_pain_points": [],
                "opportunity": raw,
                "contradictions": [],
                "key_data_points": [],
            }
