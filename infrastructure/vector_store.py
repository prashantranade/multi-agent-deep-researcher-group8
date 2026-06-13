# infrastructure/vector_store.py
import lancedb
from typing import List, Dict, Optional, Any
from langchain_openai import OpenAIEmbeddings
import config

class VectorStore:
    def __init__(self, db_path: str = None):
        self.db = lancedb.connect(db_path or config.LANCEDB_PATH)
        self.embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)

    def add_texts(self, texts: List[str], metadatas: List[Dict], table_name: str) -> None:
        vectors = self.embeddings.embed_documents(texts)
        data = [
            {"text": t, "vector": v, "metadata": m}
            for t, v, m in zip(texts, vectors, metadatas)
        ]
        if table_name in self.db.list_tables().tables:
            tbl = self.db.open_table(table_name)
            tbl.add(data)
        else:
            self.db.create_table(table_name, data=data)

    def search(
        self,
        query: str,
        table_name: str,
        k: int = 5,
        filter_source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if table_name not in self.db.list_tables().tables:
            return []
        query_vector = self.embeddings.embed_query(query)
        tbl = self.db.open_table(table_name)
        results = tbl.search(query_vector).limit(k).to_list()
        if filter_source:
            results = [r for r in results if r.get("metadata", {}).get("source") == filter_source]
        return [{"text": r["text"], "metadata": r["metadata"]} for r in results]

    def drop_table(self, table_name: str) -> None:
        if table_name in self.db.list_tables().tables:
            self.db.drop_table(table_name)
