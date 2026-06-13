# crews/bharat_desha/trend_agent.py
import json
from datetime import datetime
from tavily import TavilyClient
from infrastructure.llm_client import chat_with_fallback
import config


def run_trend_agent(topic: str) -> dict:
    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    year = datetime.now().year

    trends_results = client.search(f"{topic} India travel trends {year}", max_results=5)
    season_results = client.search(f"{topic} best time to visit India", max_results=5)

    combined = "\n\n".join(
        r["content"] for r in
        trends_results.get("results", []) + season_results.get("results", [])
        if r.get("content")
    )

    prompt = f"""You are a travel research analyst for BharatDesha, a spiritual India travel platform.

Analyse the following research about "{topic}" and return a JSON object with exactly these keys:
- "trends": list of 2-4 current trend observations (strings)
- "seasonality": object with keys "best_months" (list), "avoid_months" (list), "active_festivals" (list), "advisories" (list)
- "topic_suggestions": list of 3-5 refined topic variations the content creator can choose from

Research:
{combined}

Return only valid JSON. No markdown, no explanation."""

    response = chat_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        model=config.INTAKE_MODEL,
    )

    return json.loads(response)
