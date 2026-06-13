# crews/content_creator/retrieval_agent.py
from typing import List, Dict, Any
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore
from crews.base_crew import ResearchBrief


class CCRetrievalAgent:
    PRIORITY_SOURCES = [
        "instagram.com", "pinterest.com", "tripadvisor.com", "travelandleisure.com",
        "lonelyplanet.com", "cntraveller.com", "theguardian.com/travel",
    ]

    def __init__(self, db_path: str = None):
        self.vector_store = VectorStore(db_path=db_path)

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
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
            metadatas.append({
                "source": "user_context",
                "title": "User context",
                "domain": "user",
                "date": "2026-01-01",
            })
        if texts:
            self.vector_store.add_texts(texts, metadatas, table_name="cc_research")
        query = f"{brief.topic} for {brief.audience} in {brief.tone} tone"
        return self.vector_store.search(query, table_name="cc_research", k=10)
