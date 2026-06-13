# source_engine/scraper.py
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

_STRIP_TAGS = ["nav", "header", "footer", "script", "style", "aside", "form"]


def scrape_url(url: str, timeout: int = 10) -> str:
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(_STRIP_TAGS):
            tag.decompose()
        return " ".join(soup.get_text(separator=" ").split())
    except Exception:
        return ""


def scrape_selected_sources(sources: List[Dict]) -> List[Dict]:
    enriched = []
    for source in sources:
        content = scrape_url(source["url"])
        enriched.append({**source, "content": content})
    return enriched
