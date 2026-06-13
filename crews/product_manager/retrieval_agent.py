# crews/product_manager/retrieval_agent.py
from datetime import date
from typing import List, Dict, Any
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore
from crews.base_crew import ResearchBrief

_TABLE_NAME = "pm_research"


class PMRetrievalAgent:
    PRIORITY_SOURCES = [
        "mckinsey.com", "hbr.org", "statista.com", "bloomberg.com",
        "reuters.com", "crunchbase.com", "techcrunch.com", "forrester.com",
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
                "date": date.today().isoformat(),
            })
        if texts:
            self.vector_store.drop_table(_TABLE_NAME)
            self.vector_store.add_texts(texts, metadatas, table_name=_TABLE_NAME)
        query = f"{brief.topic} market size competition user pain points data"
        return self.vector_store.search(query, table_name=_TABLE_NAME, k=10)
