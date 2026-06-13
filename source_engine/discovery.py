# source_engine/discovery.py
from urllib.parse import urlparse
from typing import List, Dict
from tavily import TavilyClient
import config

def discover_sources(query: str, max_results: int = 10) -> List[Dict]:
    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    response = client.search(query=query, max_results=max_results, search_depth="advanced")
    results = []
    for r in response.get("results", []):
        parsed = urlparse(r.get("url", ""))
        results.append({
            "title": r.get("title", "Untitled"),
            "url": r.get("url", ""),
            "domain": parsed.netloc,
            "snippet": r.get("content", ""),
            "date": r.get("published_date", "Unknown"),
        })
    return results
