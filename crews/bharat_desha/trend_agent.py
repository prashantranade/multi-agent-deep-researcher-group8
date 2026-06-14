# crews/bharat_desha/trend_agent.py
import json
from datetime import datetime
from tavily import TavilyClient
from langchain_core.messages import HumanMessage
from infrastructure.llm_client import get_llm
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

    llm = get_llm(config.INTAKE_MODEL)
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
            "trends": [response_text] if response_text else [],
            "seasonality": {"best_months": [], "avoid_months": [], "active_festivals": [], "advisories": []},
            "topic_suggestions": [topic],
        }
