# tests/test_vector_store.py
import pytest
from unittest.mock import patch, MagicMock
from infrastructure.vector_store import VectorStore

@pytest.fixture
def mock_store(tmp_path):
    with patch("infrastructure.vector_store.OpenAIEmbeddings") as mock_emb:
        mock_emb.return_value.embed_documents.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_emb.return_value.embed_query.return_value = [0.1, 0.2, 0.3]
        store = VectorStore(db_path=str(tmp_path / "test_db"))
        yield store

def test_add_and_search_text(mock_store):
    mock_store.add_texts(
        texts=["Paris is the capital of France", "Python is a programming language"],
        metadatas=[{"source": "wiki"}, {"source": "docs"}],
        table_name="test",
    )
    results = mock_store.search("French capital city", table_name="test", k=2)
    assert len(results) >= 1
    assert "text" in results[0]
    assert "metadata" in results[0]

def test_search_empty_table_returns_empty(mock_store):
    results = mock_store.search("anything", table_name="nonexistent", k=5)
    assert results == []

def test_search_with_source_filter(mock_store):
    mock_store.add_texts(
        texts=["doc one", "doc two"],
        metadatas=[{"source": "a"}, {"source": "b"}],
        table_name="filtered",
    )
    results = mock_store.search("doc", table_name="filtered", k=5, filter_source="a")
    assert all(r["metadata"]["source"] == "a" for r in results)

def test_drop_table(mock_store):
    mock_store.add_texts(
        texts=["temp"],
        metadatas=[{"source": "x"}],
        table_name="temp_table",
    )
    assert "temp_table" in mock_store.db.list_tables().tables
    mock_store.drop_table("temp_table")
    assert "temp_table" not in mock_store.db.list_tables().tables
