import json
from typing import List, Dict
from infrastructure.llm_client import chat_with_fallback
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

    response = chat_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        model=config.ANALYSIS_MODEL,
    )

    return json.loads(response)
