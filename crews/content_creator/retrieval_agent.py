# crews/content_creator/retrieval_agent.py
from typing import List, Dict, Any
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore
from crews.base_crew import ResearchBrief
from tavily import TavilyClient
import config

_TABLE = "cc_research"


class CCRetrievalAgent:
    PRIORITY_SOURCES = [
        "instagram.com", "pinterest.com", "tripadvisor.com", "travelandleisure.com",
        "lonelyplanet.com", "cntraveller.com", "theguardian.com/travel",
    ]

    def __init__(self, db_path: str = None):
        self.vector_store = VectorStore(db_path=db_path)
        self.fallback_used = False

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        self.fallback_used = False
        enriched = scrape_selected_sources(sources)
        texts, metadatas = [], []
        for src in enriched:
            if src["content"]:
                chunks = [src["content"][i:i + 1000] for i in range(0, len(src["content"]), 1000)]
                for chunk in chunks[:5]:
                    texts.append(chunk)
                    metadatas.append({
                        "source": src["url"],
                        "title": src["title"],
                        "domain": src["domain"],
                        "date": src["date"],
                    })
        if brief.context_text:
            texts.append(brief.context_text)
            metadatas.append({"source": "user_context", "title": "User context", "domain": "user", "date": ""})

        if not texts:
            # Scraping returned nothing — fall back to Tavily web search
            self.fallback_used = True
            client = TavilyClient(api_key=config.TAVILY_API_KEY)
            results = client.search(brief.topic, max_results=6)
            for r in results.get("results", []):
                content = r.get("content", "")
                url = r.get("url", "")
                if content and url:
                    chunks = [content[i:i + 1000] for i in range(0, len(content), 1000)]
                    for chunk in chunks[:5]:
                        texts.append(chunk)
                        metadatas.append({
                            "source": url,
                            "title": r.get("title", ""),
                            "domain": url.split("/")[2] if url.startswith("http") else url,
                            "date": "",
                        })

        if texts:
            self.vector_store.drop_table(_TABLE)
            self.vector_store.add_texts(texts, metadatas, table_name=_TABLE)
        query = f"{brief.topic} for {brief.audience} in {brief.tone} tone"
        return self.vector_store.search(query, table_name=_TABLE, k=10)
