# crews/content_creator/analysis_agent.py
import json
import re
from typing import List, Dict, Any
from infrastructure.llm_client import chat_with_fallback
import config

_SYSTEM = """You are a content strategy analyst. Given research excerpts, identify:
1. Trending angles and topics resonating with the audience
2. Compelling narrative hooks and story angles
3. Audience signals — what they care about, pain points, desires
4. Tone and style notes

Return valid JSON only with keys: trends, hooks, audience_signals, tone_notes, key_facts"""


def _parse_json(raw: str) -> Dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text)


class CCAnalysisAgent:
    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        context = "\n\n".join(r["text"] for r in retrieved[:8])
        messages = [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Research excerpts:\n{context}\n\nAnalyse for content strategy:"},
        ]
        response = chat_with_fallback(messages, model=config.ANALYSIS_MODEL)
        try:
            return _parse_json(response)
        except (json.JSONDecodeError, ValueError):
            return {
                "trends": [],
                "hooks": [],
                "audience_signals": [],
                "tone_notes": response,
                "key_facts": [],
            }
