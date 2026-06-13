# crews/bharat_desha/seo_agent.py
import json
from tavily import TavilyClient
from infrastructure.llm_client import chat_with_fallback
import config


def run_seo_agent(topic: str, trend_context: dict) -> dict:
    client = TavilyClient(api_key=config.TAVILY_API_KEY)

    results = client.search(f"{topic} India travel guide", max_results=8)
    combined = "\n\n".join(
        r["content"] for r in results.get("results", []) if r.get("content")
    )

    trends_summary = ", ".join(trend_context.get("trends", []))

    prompt = f"""You are an SEO specialist for BharatDesha, a spiritual India travel platform.

Topic: "{topic}"
Current trends: {trends_summary}

Analyse the following top-ranking content and extract exactly 10 SEO keywords.

Return a JSON object with:
- "keywords": list of exactly 10 objects, each with "keyword" (string) and "intent" ("informational"|"navigational"|"transactional")
- "primary_keyword": the single most important keyword (string)

Focus on India travel, Sanatan Dharma, spiritual tourism, and wellness keywords.

Top-ranking content:
{combined}

Return only valid JSON. No markdown, no explanation."""

    response = chat_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        model=config.INTAKE_MODEL,
    )

    try:
        text = response.strip()
        if text.startswith("```"):
            import re
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text.strip())
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return {
            "keywords": [{"keyword": topic, "intent": "informational"}],
            "primary_keyword": topic,
        }
