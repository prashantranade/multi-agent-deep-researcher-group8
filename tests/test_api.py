# tests/test_api.py
import os
os.environ.setdefault("OPENROUTER_API_KEY", "x")
os.environ.setdefault("TAVILY_API_KEY", "x")

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest
from api import app

client = TestClient(app)

def test_discover_sources():
    mock_sources = [
        {"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01", "overall_score": 0.9}
    ]
    with patch("api.discover_sources", return_value=mock_sources), \
         patch("api.score_sources", return_value=mock_sources):
        response = client.post("/api/sources/discover", json={"topic": "Rajasthan travel"})
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["url"] == "https://a.com"

def test_start_research_and_polling():
    mock_output = MagicMock()
    mock_output.artifacts = [{"type": "blog_post", "content": "mock content", "citations": []}]
    mock_output.notes = ["fallback search triggered"]
    
    mock_crew = MagicMock()
    mock_crew.run.return_value = mock_output
    
    with patch("api.get_crew", return_value=mock_crew):
        # 1. Start research
        payload = {
            "topic": "Rajasthan travel",
            "persona": "content_creator",
            "audience": "millennials",
            "tone": "warm",
            "depth": "standard",
            "selected_sources": [{"url": "https://a.com"}],
            "selected_artifacts": ["blog_post"]
        }
        response = client.post("/api/research/start", json=payload)
        assert response.status_code == 200
        task = response.json()
        task_id = task["task_id"]
        assert task["status"] in ("running", "complete")

        # 2. Poll Status
        status_resp = client.get(f"/api/research/status/{task_id}")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert "status" in status_data

        # 3. Retrieve Results
        results_resp = client.get(f"/api/research/results/{task_id}")
        assert results_resp.status_code in (200, 404)
