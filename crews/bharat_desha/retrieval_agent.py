from tavily import TavilyClient
from infrastructure.vector_store import VectorStore
import config

_CHUNK_SIZE = 400

def _chunk_text(text: str, source_url: str) -> tuple:
    chunks = [text[i:i + _CHUNK_SIZE] for i in range(0, len(text), _CHUNK_SIZE) if text[i:i + _CHUNK_SIZE].strip()]
    metadatas = [{"source": source_url} for _ in chunks]
    return chunks, metadatas

def run_retrieval_agent(topic: str, seo_context: dict) -> list:
    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    primary_keyword = seo_context.get("primary_keyword", topic)

    results = client.search(f"{topic} {primary_keyword} India travel", max_results=8)

    store = VectorStore()
    for r in results.get("results", []):
        content = r.get("content", "")
        url = r.get("url", "")
        if content and url:
            chunks, metadatas = _chunk_text(content, url)
            if chunks:
                store.add_texts(chunks, metadatas, config.BHARAT_DESHA_TABLE)

    return store.search(topic, config.BHARAT_DESHA_TABLE, k=10)
