import json
from typing import List, Dict
from langchain_core.messages import HumanMessage
from infrastructure.llm_client import get_llm
import config

def run_analysis_agent(retrieved: List[Dict], seo_context: dict, trend_context: dict) -> dict:
    context = "\n\n".join(r["text"] for r in retrieved)
    keywords = ", ".join(k["keyword"] for k in seo_context.get("keywords", []))
    seasonality = trend_context.get("seasonality", {})
    festivals = ", ".join(seasonality.get("active_festivals", [])) or "none noted"
    best_months = ", ".join(seasonality.get("best_months", [])) or "year-round"

    prompt = f"""You are a senior researcher for BharatDesha, a spiritual India travel platform.

Analyse the research below through the BharatDesha lens and return a JSON object with exactly these keys:
- "spiritual": paragraph on spiritual significance (Vedic context, sacred geography, Sanatan Dharma)
- "practical": paragraph on logistics (transport, accommodation, costs, safety tips)
- "cultural": paragraph on cultural authenticity (customs, festivals, food, community)
- "wellness": paragraph on wellness angle (yoga, meditation, sound healing, Ayurveda if relevant)
- "seasonal": paragraph on best timing, festivals, and seasonal considerations
- "key_points": list of 5-8 bullet points summarising the most important takeaways
- "citations": list of source URLs from the research

SEO keywords to weave in: {keywords}
Active festivals: {festivals}
Best travel months: {best_months}

Research:
{context}

Return only valid JSON. No markdown, no explanation."""

    llm = get_llm(config.ANALYSIS_MODEL)
    response = llm.invoke([HumanMessage(content=prompt)])
    response_text = response.content

    try:
        text = response_text.strip()
        if text.startswith("```"):
            import re
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text.strip())
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return {
            "spiritual": response_text,
            "practical": "",
            "cultural": "",
            "wellness": "",
            "seasonal": "",
            "key_points": [],
            "citations": [],
        }

