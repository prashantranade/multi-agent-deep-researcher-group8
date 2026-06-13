# tests/test_formatters.py
from infrastructure.citation_formatter import format_citation, format_citation_list
from infrastructure.artifact_exporter import export_artifact, export_all_artifacts

def test_format_citation_with_all_fields():
    source = {"title": "Test Article", "url": "https://example.com", "domain": "example.com", "date": "2025-01-01"}
    result = format_citation(source, index=1)
    assert "[1]" in result
    assert "Test Article" in result
    assert "example.com" in result

def test_format_citation_missing_fields():
    result = format_citation({}, index=1)
    assert "[1]" in result
    assert "Untitled" in result

def test_format_citation_list():
    sources = [
        {"title": "A", "url": "https://a.com", "domain": "a.com", "date": "2025-01-01"},
        {"title": "B", "url": "https://b.com", "domain": "b.com", "date": "2025-01-02"},
    ]
    result = format_citation_list(sources)
    assert "[1]" in result
    assert "[2]" in result

def test_export_artifact_no_citations():
    result = export_artifact({"type": "content_brief", "content": "test content", "citations": []})
    assert "test content" in result
    assert "Sources" not in result

def test_export_artifact_with_citations():
    artifact = {
        "type": "content_brief",
        "content": "test content",
        "citations": [{"title": "A", "url": "https://a.com", "domain": "a.com", "date": "2025-01-01"}]
    }
    result = export_artifact(artifact)
    assert "test content" in result
    assert "Sources" in result
    assert "[1]" in result

def test_export_all_artifacts():
    artifacts = [
        {"type": "brief", "content": "brief content", "citations": []},
        {"type": "captions", "content": "caption content", "citations": []},
    ]
    result = export_all_artifacts(artifacts)
    assert "brief" in result
    assert "captions" in result
    assert result["brief"] == "brief content"

def test_export_all_artifacts_duplicate_types():
    artifacts = [
        {"type": "brief", "content": "first", "citations": []},
        {"type": "brief", "content": "second", "citations": []},
    ]
    result = export_all_artifacts(artifacts)
    assert "brief" in result
    assert "brief_2" in result
    assert result["brief"] == "first"
    assert result["brief_2"] == "second"
