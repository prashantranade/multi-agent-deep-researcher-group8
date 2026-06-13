# Multi-Agent Deep Researcher — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a multimodal multi-agent research assistant with persona-specific crews (Content Creator + Product Manager), guided intake, source curation with confidence scoring, and selectable artifact output.

**Architecture:** Shared intake layer routes to persona-specific LangGraph agent crews (Retrieval → Analysis → Output). All crews share underlying infrastructure tools (LanceDB, Tavily, BeautifulSoup, LangFuse). A BaseCrew abstract class defines the crew interface for plug-and-play persona extension.

**Tech Stack:** Python 3.11+, Streamlit, LangGraph, LangChain, LlamaIndex, LanceDB, Tavily API, BeautifulSoup4, LangFuse (cloud), OpenAI-compatible LLM interface (Claude Sonnet + GPT-4o mini for model routing), two-level LLM fallback (OpenRouter primary → Z.ai GLM-4.5-Air secondary)

---

## Execution order

Squad 2 (Infrastructure) **must complete Tasks 1–6b before other squads can start**. Once infrastructure is done, Squads 1, 3, and 4 work in parallel. Integration (Task 20) runs last.

```
Squad 2: Tasks 1–6b  ← start here, unblocks everything
Squad 1: Tasks 7–12  ← intake + UI
Squad 3: Tasks 13–16 ← Content Creator crew
Squad 4: Tasks 17–19 ← Product Manager crew
All:     Task 20     ← integration + Loom prep
Squad 2: Task 21     ← production deployment setup
```

---

## File structure

```
deep-researcher/
├── app.py                              # Streamlit entry point — Squad 1
├── config.py                           # Model config, env-aware loading — Squad 2
├── requirements.txt                    # Squad 2
├── Dockerfile                          # Squad 2 — production container
├── docker-compose.yml                  # Squad 2 — local Docker testing
├── .dockerignore                       # Squad 2
├── .gitignore                          # Squad 2
├── .env.local.example                  # Squad 2 — committed template for local dev
├── .env.production.example             # Squad 2 — committed template for production
├── .streamlit/
│   └── config.toml                     # Squad 2 — Streamlit server settings
│
├── intake/
│   ├── __init__.py
│   ├── persona_selector.py             # Squad 1
│   ├── topic_intake.py                 # Squad 1
│   ├── context_enrichment.py           # Squad 1 (multimodal: docs, URL, handle)
│   └── clarification_agent.py          # Squad 1
│
├── source_engine/
│   ├── __init__.py
│   ├── discovery.py                    # Squad 1 (Tavily)
│   ├── scraper.py                      # Squad 1 (BeautifulSoup)
│   └── confidence_scorer.py           # Squad 1
│
├── crews/
│   ├── __init__.py
│   ├── base_crew.py                    # Squad 2 (shared contract)
│   ├── content_creator/
│   │   ├── __init__.py
│   │   ├── retrieval_agent.py          # Squad 3
│   │   ├── analysis_agent.py           # Squad 3
│   │   └── output_agent.py             # Squad 3
│   └── product_manager/
│       ├── __init__.py
│       ├── retrieval_agent.py          # Squad 4
│       ├── analysis_agent.py           # Squad 4
│       └── output_agent.py             # Squad 4
│
├── infrastructure/
│   ├── __init__.py
│   ├── llm_client.py                   # Squad 2 (fallback LLM client — OpenRouter → Z.ai)
│   ├── vector_store.py                 # Squad 2 (LanceDB wrapper)
│   ├── pdf_parser.py                   # Squad 2
│   ├── image_analyser.py               # Squad 2
│   ├── citation_formatter.py           # Squad 2
│   └── artifact_exporter.py            # Squad 2
│
├── observability/
│   ├── __init__.py
│   └── langfuse_client.py              # Squad 2
│
└── outputs/
    ├── content_creator/
    │   └── templates.py                # Squad 3
    └── product_manager/
        └── templates.py                # Squad 4
```

---

## SQUAD 2 — Infrastructure (start here)

### Task 1: Project setup + config

**Files:**
- Create: `requirements.txt`
- Create: `.env.local.example`
- Create: `.env.production.example`
- Create: `.gitignore`
- Create: `config.py`

- [ ] **Step 1: Create requirements.txt**

```
streamlit>=1.35.0
langchain>=0.2.0
langchain-openai>=0.1.0
langchain-anthropic>=0.1.0
langgraph>=0.1.0
llama-index>=0.10.0
lancedb>=0.8.0
langfuse>=2.0.0
tavily-python>=0.3.0
beautifulsoup4>=4.12.0
requests>=2.31.0
pypdf>=4.0.0
python-docx>=1.1.0
pillow>=10.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

- [ ] **Step 2: Create .env.local.example**

```
# Local development environment
APP_ENV=local
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
ZAI_API_KEY=...
TAVILY_API_KEY=tvly-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
LANCEDB_PATH=.lancedb_local
```

- [ ] **Step 3: Create .env.production.example**

```
# Production environment — fill in before deploying
APP_ENV=production
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
ZAI_API_KEY=...
TAVILY_API_KEY=tvly-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
LANCEDB_PATH=/data/lancedb
```

- [ ] **Step 4: Create .gitignore**

```
.env.local
.env.production
.lancedb_local/
/data/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
```

- [ ] **Step 5: Create config.py**

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load the right env file based on APP_ENV (default: local)
APP_ENV = os.getenv("APP_ENV", "local")
env_file = Path(f".env.{APP_ENV}")
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()  # fallback to plain .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ZAI_API_KEY = os.getenv("ZAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
LANCEDB_PATH = os.getenv("LANCEDB_PATH", ".lancedb_local")

# Model routing — fast/cheap for intake, powerful for analysis
INTAKE_MODEL = "gpt-4o-mini"
ANALYSIS_MODEL = "claude-sonnet-4-6"
OUTPUT_MODEL = "claude-sonnet-4-6"

AVAILABLE_MODELS = {
    "Fast (GPT-4o mini)": "gpt-4o-mini",
    "Balanced (GPT-4o)": "gpt-4o",
    "Thorough (Claude Sonnet)": "claude-sonnet-4-6",
}
```

- [ ] **Step 6: Create .env.local from example and fill in API keys**

```bash
cp .env.local.example .env.local
# Fill in your actual API keys in .env.local
```

- [ ] **Step 7: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 8: Verify env loading works**

```bash
python -c "import config; print('ENV:', config.APP_ENV); print('DB path:', config.LANCEDB_PATH)"
```
Expected output:
```
ENV: local
DB path: .lancedb_local
```

- [ ] **Step 9: Commit**

```bash
git add requirements.txt .env.local.example .env.production.example .gitignore config.py
git commit -m "feat: env-aware config — local and production environment separation"
```

---

### Task 2: LangFuse observability client

**Files:**
- Create: `observability/__init__.py`
- Create: `observability/langfuse_client.py`
- Create: `tests/test_langfuse_client.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_langfuse_client.py
from unittest.mock import patch, MagicMock
from observability.langfuse_client import get_langfuse_handler, trace_agent_run

def test_get_langfuse_handler_returns_handler():
    with patch("observability.langfuse_client.CallbackHandler") as mock_cb:
        mock_cb.return_value = MagicMock()
        handler = get_langfuse_handler(session_id="test-123", user_id="user-1")
        assert handler is not None
        mock_cb.assert_called_once()

def test_trace_agent_run_wraps_function():
    called = {}
    def my_fn(*args, **kwargs):
        called["yes"] = True
        return "result"
    wrapped = trace_agent_run("test-agent")(my_fn)
    result = wrapped()
    assert called.get("yes") is True
    assert result == "result"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_langfuse_client.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create observability/__init__.py**

```python
```

- [ ] **Step 4: Implement langfuse_client.py**

```python
# observability/langfuse_client.py
import functools
from langfuse.callback import CallbackHandler
import config

def get_langfuse_handler(session_id: str, user_id: str = "anonymous") -> CallbackHandler:
    return CallbackHandler(
        secret_key=config.LANGFUSE_SECRET_KEY,
        public_key=config.LANGFUSE_PUBLIC_KEY,
        host=config.LANGFUSE_HOST,
        session_id=session_id,
        user_id=user_id,
    )

def trace_agent_run(agent_name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_langfuse_client.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add observability/ tests/test_langfuse_client.py
git commit -m "feat: LangFuse observability client"
```

---

### Task 3: LanceDB vector store wrapper

**Files:**
- Create: `infrastructure/__init__.py`
- Create: `infrastructure/vector_store.py`
- Create: `tests/test_vector_store.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_vector_store.py
import pytest
import tempfile
import os
from infrastructure.vector_store import VectorStore

@pytest.fixture
def tmp_store(tmp_path):
    return VectorStore(db_path=str(tmp_path / "test_db"))

def test_add_and_search_text(tmp_store):
    tmp_store.add_texts(
        texts=["Paris is the capital of France", "Python is a programming language"],
        metadatas=[{"source": "wiki"}, {"source": "docs"}],
        table_name="test",
    )
    results = tmp_store.search("French capital city", table_name="test", k=1)
    assert len(results) == 1
    assert "Paris" in results[0]["text"]

def test_search_with_source_filter(tmp_store):
    tmp_store.add_texts(
        texts=["doc one", "doc two"],
        metadatas=[{"source": "a"}, {"source": "b"}],
        table_name="filtered",
    )
    results = tmp_store.search("doc", table_name="filtered", k=5, filter_source="a")
    assert all(r["metadata"]["source"] == "a" for r in results)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_vector_store.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement infrastructure/__init__.py**

```python
```

- [ ] **Step 4: Implement vector_store.py**

```python
# infrastructure/vector_store.py
import lancedb
import numpy as np
from typing import List, Dict, Optional, Any
from lancedb.pydantic import LanceModel, Vector
from langchain_openai import OpenAIEmbeddings
import config

class VectorStore:
    def __init__(self, db_path: str = ".lancedb"):
        self.db = lancedb.connect(db_path)
        self.embeddings = OpenAIEmbeddings(api_key=config.OPENAI_API_KEY)

    def add_texts(self, texts: List[str], metadatas: List[Dict], table_name: str) -> None:
        vectors = self.embeddings.embed_documents(texts)
        data = [
            {"text": t, "vector": v, "metadata": m}
            for t, v, m in zip(texts, vectors, metadatas)
        ]
        if table_name in self.db.table_names():
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
        if table_name not in self.db.table_names():
            return []
        query_vector = self.embeddings.embed_query(query)
        tbl = self.db.open_table(table_name)
        results = tbl.search(query_vector).limit(k).to_list()
        if filter_source:
            results = [r for r in results if r.get("metadata", {}).get("source") == filter_source]
        return [{"text": r["text"], "metadata": r["metadata"]} for r in results]

    def drop_table(self, table_name: str) -> None:
        if table_name in self.db.table_names():
            self.db.drop_table(table_name)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_vector_store.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add infrastructure/ tests/test_vector_store.py
git commit -m "feat: LanceDB vector store wrapper with source filtering"
```

---

### Task 4: PDF, document, and image parsers

**Files:**
- Create: `infrastructure/pdf_parser.py`
- Create: `infrastructure/image_analyser.py`
- Create: `tests/test_parsers.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_parsers.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from infrastructure.pdf_parser import parse_pdf, parse_docx
from infrastructure.image_analyser import analyse_image

def test_parse_pdf_returns_text(tmp_path):
    # Create a minimal PDF-like test using mock
    with patch("infrastructure.pdf_parser.PdfReader") as mock_reader:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Hello from PDF"
        mock_reader.return_value.pages = [mock_page]
        result = parse_pdf("fake.pdf")
    assert "Hello from PDF" in result

def test_parse_docx_returns_text(tmp_path):
    with patch("infrastructure.pdf_parser.Document") as mock_doc:
        mock_para = MagicMock()
        mock_para.text = "Hello from DOCX"
        mock_doc.return_value.paragraphs = [mock_para]
        result = parse_docx("fake.docx")
    assert "Hello from DOCX" in result

def test_analyse_image_returns_description():
    with patch("infrastructure.image_analyser.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = "A mountain landscape"
        result = analyse_image("fake_image.png")
    assert isinstance(result, str)
    assert len(result) > 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_parsers.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement pdf_parser.py**

```python
# infrastructure/pdf_parser.py
from pypdf import PdfReader
from docx import Document

def parse_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def parse_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

def parse_uploaded_file(file_path: str, mime_type: str) -> str:
    if mime_type == "application/pdf":
        return parse_pdf(file_path)
    elif mime_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ):
        return parse_docx(file_path)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
```

- [ ] **Step 4: Implement image_analyser.py**

```python
# infrastructure/image_analyser.py
import base64
from openai import OpenAI
import config

def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyse_image(image_path: str) -> str:
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    b64 = _encode_image(image_path)
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = f"image/{ext}" if ext in ("png", "jpg", "jpeg", "gif", "webp") else "image/png"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                {"type": "text", "text": "Describe the content of this image in detail for use as research context."},
            ],
        }],
        max_tokens=500,
    )
    return response.choices[0].message.content
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_parsers.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add infrastructure/pdf_parser.py infrastructure/image_analyser.py tests/test_parsers.py
git commit -m "feat: PDF, DOCX, and image parsers"
```

---

### Task 5: Citation formatter and artifact exporter

**Files:**
- Create: `infrastructure/citation_formatter.py`
- Create: `infrastructure/artifact_exporter.py`
- Create: `tests/test_formatters.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_formatters.py
from infrastructure.citation_formatter import format_citation, format_citation_list
from infrastructure.artifact_exporter import export_artifact

def test_format_citation_with_all_fields():
    source = {"title": "Test Article", "url": "https://example.com", "domain": "example.com", "date": "2025-01-01"}
    result = format_citation(source, index=1)
    assert "[1]" in result
    assert "Test Article" in result
    assert "example.com" in result

def test_format_citation_list():
    sources = [
        {"title": "A", "url": "https://a.com", "domain": "a.com", "date": "2025-01-01"},
        {"title": "B", "url": "https://b.com", "domain": "b.com", "date": "2025-01-02"},
    ]
    result = format_citation_list(sources)
    assert "[1]" in result
    assert "[2]" in result

def test_export_artifact_returns_string():
    result = export_artifact({"type": "content_brief", "content": "test content", "citations": []})
    assert isinstance(result, str)
    assert "test content" in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_formatters.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement citation_formatter.py**

```python
# infrastructure/citation_formatter.py
from typing import List, Dict

def format_citation(source: Dict, index: int) -> str:
    title = source.get("title", "Untitled")
    url = source.get("url", "")
    domain = source.get("domain", "")
    date = source.get("date", "n.d.")
    return f"[{index}] {title} — {domain} ({date})\n    {url}"

def format_citation_list(sources: List[Dict]) -> str:
    return "\n".join(format_citation(s, i + 1) for i, s in enumerate(sources))
```

- [ ] **Step 4: Implement artifact_exporter.py**

```python
# infrastructure/artifact_exporter.py
from typing import Dict, Any
from infrastructure.citation_formatter import format_citation_list

def export_artifact(artifact: Dict[str, Any]) -> str:
    artifact_type = artifact.get("type", "research")
    content = artifact.get("content", "")
    citations = artifact.get("citations", [])
    citation_block = f"\n\n---\n**Sources**\n{format_citation_list(citations)}" if citations else ""
    return f"{content}{citation_block}"

def export_all_artifacts(artifacts: List[Dict[str, Any]]) -> Dict[str, str]:
    return {a["type"]: export_artifact(a) for a in artifacts}
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_formatters.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add infrastructure/citation_formatter.py infrastructure/artifact_exporter.py tests/test_formatters.py
git commit -m "feat: citation formatter and artifact exporter"
```

---

### Task 6: BaseCrew abstract class

**Files:**
- Create: `crews/__init__.py`
- Create: `crews/base_crew.py`
- Create: `tests/test_base_crew.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_base_crew.py
import pytest
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput

def test_base_crew_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        BaseCrew()

def test_concrete_crew_must_implement_all_methods():
    class IncompleteCrew(BaseCrew):
        def retrieve(self, brief, sources):
            return []
        # missing analyse and generate_artifacts

    with pytest.raises(TypeError):
        IncompleteCrew()

def test_concrete_crew_works_when_fully_implemented():
    class MockCrew(BaseCrew):
        def retrieve(self, brief, sources):
            return [{"text": "retrieved", "metadata": {}}]
        def analyse(self, retrieved):
            return {"summary": "analysis done"}
        def generate_artifacts(self, analysis, selected_artifacts):
            return [{"type": "brief", "content": "output", "citations": []}]

    crew = MockCrew()
    brief = ResearchBrief(topic="test", persona="content_creator", audience="general", tone="neutral", depth="standard")
    retrieved = crew.retrieve(brief, sources=[])
    analysis = crew.analyse(retrieved)
    artifacts = crew.generate_artifacts(analysis, selected_artifacts=["brief"])
    assert artifacts[0]["content"] == "output"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_base_crew.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Create crews/__init__.py**

```python
```

- [ ] **Step 4: Implement base_crew.py**

```python
# crews/base_crew.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ResearchBrief:
    topic: str
    persona: str                        # "content_creator" | "product_manager"
    audience: str
    tone: str
    depth: str                          # "quick" | "standard" | "deep"
    context_text: Optional[str] = None  # from uploaded docs / URL / social handle
    selected_sources: List[Dict] = field(default_factory=list)
    selected_artifacts: List[str] = field(default_factory=list)

@dataclass
class CrewOutput:
    artifacts: List[Dict[str, Any]]     # [{"type": str, "content": str, "citations": List}]
    trace_id: Optional[str] = None

class BaseCrew(ABC):
    """
    All persona crews implement this interface.
    Adding a new persona = subclass BaseCrew, implement three methods, done.
    """

    @abstractmethod
    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        """Retrieve and chunk content from selected sources into the vector store."""
        ...

    @abstractmethod
    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyse retrieved content through a persona-specific lens."""
        ...

    @abstractmethod
    def generate_artifacts(
        self, analysis: Dict[str, Any], selected_artifacts: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate only the selected artifact types from the analysis."""
        ...

    def run(self, brief: ResearchBrief) -> CrewOutput:
        retrieved = self.retrieve(brief, brief.selected_sources)
        analysis = self.analyse(retrieved)
        artifacts = self.generate_artifacts(analysis, brief.selected_artifacts)
        return CrewOutput(artifacts=artifacts)
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_base_crew.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add crews/ tests/test_base_crew.py
git commit -m "feat: BaseCrew abstract class — plug-and-play persona contract"
```

---

---

### Task 6b: Fallback LLM client

**Files:**
- Create: `infrastructure/llm_client.py`
- Create: `tests/test_llm_client.py`

Two-level fallback chain: OpenRouter (primary, full model quality) → Z.ai GLM-4.5-Air (secondary, free tier). Catches `RateLimitError` and `APIStatusError` on the primary, retries on the secondary. All crews use this client instead of calling LangChain LLM wrappers directly.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_llm_client.py
from unittest.mock import patch, MagicMock, call
import openai
from infrastructure.llm_client import chat_with_fallback

def test_primary_succeeds_no_fallback():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "primary response"
    with patch("infrastructure.llm_client._call_provider") as mock_call:
        mock_call.return_value = mock_response
        result = chat_with_fallback(messages=[{"role": "user", "content": "hello"}], model="claude-sonnet-4-6")
    assert result == "primary response"
    assert mock_call.call_count == 1

def test_primary_rate_limit_triggers_fallback():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "fallback response"
    with patch("infrastructure.llm_client._call_provider") as mock_call:
        mock_call.side_effect = [
            openai.RateLimitError("rate limit", response=MagicMock(), body={}),
            mock_response,
        ]
        result = chat_with_fallback(messages=[{"role": "user", "content": "hello"}], model="claude-sonnet-4-6")
    assert result == "fallback response"
    assert mock_call.call_count == 2

def test_both_providers_fail_raises():
    with patch("infrastructure.llm_client._call_provider") as mock_call:
        mock_call.side_effect = openai.RateLimitError("rate limit", response=MagicMock(), body={})
        import pytest
        with pytest.raises(RuntimeError, match="All LLM providers exhausted"):
            chat_with_fallback(messages=[{"role": "user", "content": "hello"}], model="claude-sonnet-4-6")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_llm_client.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement infrastructure/llm_client.py**

```python
# infrastructure/llm_client.py
from typing import List, Dict, Any
import openai
import config

_PROVIDERS = [
    {
        "name": "openrouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_attr": "OPENROUTER_API_KEY",
        "model_override": None,          # use the model requested as-is
    },
    {
        "name": "zai",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "api_key_attr": "ZAI_API_KEY",
        "model_override": "glm-4-air",  # Z.ai free fallback model
    },
]

def _call_provider(provider: Dict, messages: List[Dict], model: str) -> Any:
    client = openai.OpenAI(
        api_key=getattr(config, provider["api_key_attr"]),
        base_url=provider["base_url"],
    )
    effective_model = provider["model_override"] or model
    return client.chat.completions.create(
        model=effective_model,
        messages=messages,
    )

def chat_with_fallback(messages: List[Dict[str, str]], model: str) -> str:
    last_error = None
    for provider in _PROVIDERS:
        try:
            response = _call_provider(provider, messages, model)
            return response.choices[0].message.content
        except (openai.RateLimitError, openai.APIStatusError) as e:
            last_error = e
            continue
    raise RuntimeError(f"All LLM providers exhausted. Last error: {last_error}")
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_llm_client.py -v
```
Expected: PASS

- [ ] **Step 5: Update requirements.txt — add openai SDK**

Add to requirements.txt if not already present:
```
openai>=1.30.0
```

Run:
```bash
pip install openai
```

- [ ] **Step 6: Commit**

```bash
git add infrastructure/llm_client.py tests/test_llm_client.py requirements.txt
git commit -m "feat: two-level LLM fallback — OpenRouter primary, Z.ai GLM-4.5-Air secondary"
```

---

## SQUAD 1 — Intake + Source Engine + UI

> **Prerequisite:** Tasks 6 and 6b must be complete (BaseCrew + LLM client available). Use mock crew responses while Squads 3/4 build.

### Task 7: Tavily source discovery

**Files:**
- Create: `source_engine/__init__.py`
- Create: `source_engine/discovery.py`
- Create: `tests/test_discovery.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_discovery.py
from unittest.mock import patch, MagicMock
from source_engine.discovery import discover_sources

def test_discover_sources_returns_list():
    with patch("source_engine.discovery.TavilyClient") as mock_tavily:
        mock_client = MagicMock()
        mock_tavily.return_value = mock_client
        mock_client.search.return_value = {
            "results": [
                {"title": "Article A", "url": "https://a.com", "content": "text a", "published_date": "2025-01-01"},
                {"title": "Article B", "url": "https://b.com", "content": "text b", "published_date": "2025-01-02"},
            ]
        }
        results = discover_sources("sustainable travel Rajasthan", max_results=2)
    assert len(results) == 2
    assert results[0]["title"] == "Article A"
    assert "domain" in results[0]

def test_discover_sources_extracts_domain():
    with patch("source_engine.discovery.TavilyClient") as mock_tavily:
        mock_client = MagicMock()
        mock_tavily.return_value = mock_client
        mock_client.search.return_value = {
            "results": [{"title": "T", "url": "https://bbc.co.uk/news/article", "content": "c", "published_date": "2025-01-01"}]
        }
        results = discover_sources("test", max_results=1)
    assert results[0]["domain"] == "bbc.co.uk"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_discovery.py -v
```
Expected: FAIL

- [ ] **Step 3: Create source_engine/__init__.py**

```python
```

- [ ] **Step 4: Implement discovery.py**

```python
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
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_discovery.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add source_engine/ tests/test_discovery.py
git commit -m "feat: Tavily source discovery"
```

---

### Task 8: BeautifulSoup deep scraper

**Files:**
- Create: `source_engine/scraper.py`
- Create: `tests/test_scraper.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scraper.py
from unittest.mock import patch, MagicMock
from source_engine.scraper import scrape_url, scrape_selected_sources

def test_scrape_url_extracts_text():
    mock_html = "<html><body><p>This is article content.</p><nav>nav</nav></body></html>"
    with patch("source_engine.scraper.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = mock_html
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        result = scrape_url("https://example.com")
    assert "article content" in result
    assert "nav" not in result  # nav tags stripped

def test_scrape_url_handles_failure():
    with patch("source_engine.scraper.requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")
        result = scrape_url("https://bad-url.com")
    assert result == ""

def test_scrape_selected_sources_returns_dict():
    sources = [{"url": "https://a.com", "title": "A"}, {"url": "https://b.com", "title": "B"}]
    with patch("source_engine.scraper.scrape_url") as mock_scrape:
        mock_scrape.return_value = "scraped content"
        result = scrape_selected_sources(sources)
    assert len(result) == 2
    assert result[0]["content"] == "scraped content"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_scraper.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement scraper.py**

```python
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
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_scraper.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add source_engine/scraper.py tests/test_scraper.py
git commit -m "feat: BeautifulSoup deep scraper for selected sources"
```

---

### Task 9: Confidence scorer

**Files:**
- Create: `source_engine/confidence_scorer.py`
- Create: `tests/test_confidence_scorer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_confidence_scorer.py
from source_engine.confidence_scorer import score_source, score_sources, TRUSTED_DOMAINS

def test_score_source_returns_all_parameters():
    source = {
        "title": "Test", "url": "https://bbc.com/article", "domain": "bbc.com",
        "snippet": "some content here", "date": "2025-06-01"
    }
    scored = score_source(source)
    assert "recency_score" in scored
    assert "domain_score" in scored
    assert "relevance_score" in scored
    assert "overall_score" in scored
    assert 0.0 <= scored["overall_score"] <= 1.0

def test_trusted_domain_gets_high_domain_score():
    source = {"title": "T", "url": "https://bbc.com/a", "domain": "bbc.com", "snippet": "x", "date": "2025-01-01"}
    scored = score_source(source)
    assert scored["domain_score"] >= 0.8

def test_unknown_domain_gets_lower_score():
    source = {"title": "T", "url": "https://randomsite123.com/a", "domain": "randomsite123.com", "snippet": "x", "date": "2025-01-01"}
    scored = score_source(source)
    assert scored["domain_score"] < 0.8

def test_score_sources_sorts_by_overall_score():
    sources = [
        {"title": "A", "url": "https://randomsite.com/a", "domain": "randomsite.com", "snippet": "x", "date": "2020-01-01"},
        {"title": "B", "url": "https://bbc.com/a", "domain": "bbc.com", "snippet": "y", "date": "2025-06-01"},
    ]
    scored = score_sources(sources)
    assert scored[0]["overall_score"] >= scored[1]["overall_score"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_confidence_scorer.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement confidence_scorer.py**

```python
# source_engine/confidence_scorer.py
from datetime import datetime
from typing import List, Dict, Any

TRUSTED_DOMAINS = {
    "bbc.com", "reuters.com", "nytimes.com", "theguardian.com", "bloomberg.com",
    "economist.com", "nature.com", "sciencedirect.com", "pubmed.ncbi.nlm.nih.gov",
    "hbr.org", "mckinsey.com", "wikipedia.org", "britannica.com",
    "gov.in", "nic.in", "who.int", "worldbank.org",
}

def _recency_score(date_str: str) -> float:
    try:
        pub_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        days_old = (datetime.now() - pub_date).days
        if days_old <= 90: return 1.0
        if days_old <= 365: return 0.8
        if days_old <= 730: return 0.6
        if days_old <= 1825: return 0.4
        return 0.2
    except Exception:
        return 0.3

def _domain_score(domain: str) -> float:
    clean = domain.replace("www.", "")
    for trusted in TRUSTED_DOMAINS:
        if clean == trusted or clean.endswith(f".{trusted}"):
            return 1.0
    if clean.endswith((".gov", ".edu", ".ac.uk", ".ac.in")):
        return 0.9
    if clean.endswith((".org", ".int")):
        return 0.7
    return 0.5

def _relevance_score(snippet: str) -> float:
    word_count = len(snippet.split())
    if word_count >= 200: return 1.0
    if word_count >= 100: return 0.8
    if word_count >= 50: return 0.6
    if word_count >= 10: return 0.4
    return 0.2

def score_source(source: Dict[str, Any]) -> Dict[str, Any]:
    recency = _recency_score(source.get("date", ""))
    domain = _domain_score(source.get("domain", ""))
    relevance = _relevance_score(source.get("snippet", ""))
    overall = round((recency * 0.3) + (domain * 0.4) + (relevance * 0.3), 2)
    return {**source, "recency_score": recency, "domain_score": domain, "relevance_score": relevance, "overall_score": overall}

def score_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored = [score_source(s) for s in sources]
    return sorted(scored, key=lambda x: x["overall_score"], reverse=True)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_confidence_scorer.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add source_engine/confidence_scorer.py tests/test_confidence_scorer.py
git commit -m "feat: confidence scorer with recency, domain authority, relevance"
```

---

### Task 10: Clarification agent

**Files:**
- Create: `intake/__init__.py`
- Create: `intake/clarification_agent.py`
- Create: `tests/test_clarification_agent.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_clarification_agent.py
from unittest.mock import patch, MagicMock
from intake.clarification_agent import ClarificationAgent
from crews.base_crew import ResearchBrief

def test_clarification_agent_returns_brief():
    with patch("intake.clarification_agent.ChatOpenAI") as mock_llm:
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance
        mock_instance.invoke.return_value.content = '{"audience": "millennials", "tone": "inspirational", "depth": "standard"}'
        agent = ClarificationAgent(model="gpt-4o-mini")
        brief = agent.build_brief(
            topic="sustainable travel Rajasthan",
            persona="content_creator",
            context_text="BharatDesha travel site for India content",
            answers={"audience": "millennials", "tone": "inspirational"},
        )
    assert isinstance(brief, ResearchBrief)
    assert brief.topic == "sustainable travel Rajasthan"
    assert brief.persona == "content_creator"

def test_clarification_agent_generates_questions():
    with patch("intake.clarification_agent.ChatOpenAI") as mock_llm:
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance
        mock_instance.invoke.return_value.content = '["Who is your target audience?"]'
        agent = ClarificationAgent(model="gpt-4o-mini")
        questions = agent.get_next_question(
            topic="sustainable travel",
            persona="content_creator",
            context_text=None,
            answers_so_far={},
        )
    assert isinstance(questions, str)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_clarification_agent.py -v
```
Expected: FAIL

- [ ] **Step 3: Create intake/__init__.py**

```python
```

- [ ] **Step 4: Implement clarification_agent.py**

```python
# intake/clarification_agent.py
import json
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from crews.base_crew import ResearchBrief
import config

_SYSTEM_PROMPT = """You are a research intake assistant. Your job is to understand what a user needs to research and build a clear research brief.
Ask targeted questions one at a time. If context is provided (e.g. website content, social handle), use it to infer answers and skip those questions.
Always respond with valid JSON only."""

class ClarificationAgent:
    def __init__(self, model: str = None):
        self.llm = ChatOpenAI(
            model=model or config.INTAKE_MODEL,
            api_key=config.OPENAI_API_KEY,
            temperature=0.3,
        )

    def get_next_question(
        self, topic: str, persona: str, context_text: Optional[str], answers_so_far: Dict
    ) -> Optional[str]:
        context_block = f"\nContext already provided:\n{context_text[:500]}" if context_text else ""
        answers_block = f"\nAnswers collected so far: {json.dumps(answers_so_far)}" if answers_so_far else ""
        needed = [q for q in ["audience", "tone", "depth"] if q not in answers_so_far]
        if not needed:
            return None
        prompt = f"""Topic: {topic}\nPersona: {persona}{context_block}{answers_block}
Next question to ask (return ONLY a plain string, one question):
Still needed: {needed}
If context already answers any of these, skip them and return null."""
        response = self.llm.invoke([SystemMessage(content=_SYSTEM_PROMPT), HumanMessage(content=prompt)])
        content = response.content.strip()
        if content.lower() in ("null", "none", ""):
            return None
        return content.strip('"').strip("'")

    def build_brief(
        self, topic: str, persona: str, context_text: Optional[str], answers: Dict
    ) -> ResearchBrief:
        return ResearchBrief(
            topic=topic,
            persona=persona,
            audience=answers.get("audience", "general audience"),
            tone=answers.get("tone", "neutral"),
            depth=answers.get("depth", "standard"),
            context_text=context_text,
        )
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_clarification_agent.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add intake/ tests/test_clarification_agent.py
git commit -m "feat: clarification agent — builds research brief from topic + context"
```

---

### Task 11: Context enrichment (multimodal intake)

**Files:**
- Create: `intake/context_enrichment.py`
- Create: `tests/test_context_enrichment.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_context_enrichment.py
from unittest.mock import patch, MagicMock
from intake.context_enrichment import enrich_from_url, enrich_from_file, build_context_text

def test_enrich_from_url_returns_text():
    with patch("intake.context_enrichment.scrape_url") as mock_scrape:
        mock_scrape.return_value = "This is website content about India travel."
        result = enrich_from_url("https://bharatdesha.com")
    assert "India travel" in result

def test_enrich_from_url_handles_failure():
    with patch("intake.context_enrichment.scrape_url") as mock_scrape:
        mock_scrape.return_value = ""
        result = enrich_from_url("https://broken.com")
    assert result == ""

def test_build_context_text_combines_sources():
    result = build_context_text(url_text="URL content", file_text="File content", handle_text="Handle content")
    assert "URL content" in result
    assert "File content" in result
    assert "Handle content" in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_context_enrichment.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement context_enrichment.py**

```python
# intake/context_enrichment.py
import tempfile
import os
from typing import Optional
from source_engine.scraper import scrape_url
from infrastructure.pdf_parser import parse_uploaded_file
from infrastructure.image_analyser import analyse_image

def enrich_from_url(url: str) -> str:
    return scrape_url(url)[:3000]

def enrich_from_file(file_bytes: bytes, filename: str, mime_type: str) -> str:
    suffix = f".{filename.rsplit('.', 1)[-1]}" if "." in filename else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        if mime_type.startswith("image/"):
            return analyse_image(tmp_path)
        return parse_uploaded_file(tmp_path, mime_type)[:3000]
    finally:
        os.unlink(tmp_path)

def enrich_from_handle(handle: str) -> str:
    # Social handle enrichment — for hackathon, scrape profile URL or return handle as context
    cleaned = handle.lstrip("@")
    return f"Social media creator handle: @{cleaned}. Research should be tailored to this creator's style."

def build_context_text(
    url_text: str = "",
    file_text: str = "",
    handle_text: str = "",
) -> str:
    parts = []
    if url_text: parts.append(f"Website content:\n{url_text}")
    if file_text: parts.append(f"Uploaded document:\n{file_text}")
    if handle_text: parts.append(f"Social context:\n{handle_text}")
    return "\n\n".join(parts)
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_context_enrichment.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add intake/context_enrichment.py tests/test_context_enrichment.py
git commit -m "feat: multimodal context enrichment — URL, file, social handle"
```

---

### Task 12: Streamlit app — full UI flow

**Files:**
- Create: `app.py`

- [ ] **Step 1: Implement app.py**

```python
# app.py
import streamlit as st
import uuid
from intake.clarification_agent import ClarificationAgent
from intake.context_enrichment import enrich_from_url, enrich_from_file, enrich_from_handle, build_context_text
from source_engine.discovery import discover_sources
from source_engine.confidence_scorer import score_sources
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore
from infrastructure.artifact_exporter import export_artifact
from observability.langfuse_client import get_langfuse_handler
import config

# Lazy import crews so squads can work independently
def _load_crew(persona: str):
    if persona == "content_creator":
        from crews.content_creator.retrieval_agent import CCRetrievalAgent
        from crews.content_creator.analysis_agent import CCAnalysisAgent
        from crews.content_creator.output_agent import CCOutputAgent
        class CCCrew:
            def __init__(self):
                self.retrieval = CCRetrievalAgent()
                self.analysis = CCAnalysisAgent()
                self.output = CCOutputAgent()
            def run(self, brief):
                retrieved = self.retrieval.retrieve(brief, brief.selected_sources)
                analysis = self.analysis.analyse(retrieved)
                return self.output.generate_artifacts(analysis, brief.selected_artifacts)
        return CCCrew()
    elif persona == "product_manager":
        from crews.product_manager.retrieval_agent import PMRetrievalAgent
        from crews.product_manager.analysis_agent import PMAnalysisAgent
        from crews.product_manager.output_agent import PMOutputAgent
        class PMCrew:
            def __init__(self):
                self.retrieval = PMRetrievalAgent()
                self.analysis = PMAnalysisAgent()
                self.output = PMOutputAgent()
            def run(self, brief):
                retrieved = self.retrieval.retrieve(brief, brief.selected_sources)
                analysis = self.analysis.analyse(retrieved)
                return self.output.generate_artifacts(analysis, brief.selected_artifacts)
        return PMCrew()

st.set_page_config(page_title="Deep Researcher", layout="wide")
st.title("Multi-Agent Deep Researcher")
st.caption("Persona-aware · source-verified · multimodal")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "context_text" not in st.session_state:
    st.session_state.context_text = ""
if "brief" not in st.session_state:
    st.session_state.brief = None
if "sources" not in st.session_state:
    st.session_state.sources = []

# ── STEP 1: Persona ──────────────────────────────────────────────────────────
with st.expander("Step 1 — Select your persona", expanded=st.session_state.step == 1):
    persona = st.radio("I am a...", ["Content Creator", "Product Manager"], horizontal=True)
    if st.button("Continue →", key="step1"):
        st.session_state.persona = "content_creator" if "Creator" in persona else "product_manager"
        st.session_state.step = 2
        st.rerun()

# ── STEP 2: Topic ─────────────────────────────────────────────────────────────
if st.session_state.step >= 2:
    with st.expander("Step 2 — What do you want to research?", expanded=st.session_state.step == 2):
        topic = st.text_input("Research topic", placeholder="e.g. Sustainable travel in Rajasthan for millennials")
        if st.button("Continue →", key="step2") and topic:
            st.session_state.topic = topic
            st.session_state.step = 3
            st.rerun()

# ── STEP 3: Context enrichment ───────────────────────────────────────────────
if st.session_state.step >= 3:
    with st.expander("Step 3 — Add context (optional)", expanded=st.session_state.step == 3):
        url_input = st.text_input("Your website or relevant URL", placeholder="https://bharatdesha.com")
        handle_input = st.text_input("Social media handle", placeholder="@bharatdesha")
        uploaded_files = st.file_uploader("Upload documents or images", accept_multiple_files=True,
                                          type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
        if st.button("Continue →", key="step3"):
            url_text = enrich_from_url(url_input) if url_input else ""
            handle_text = enrich_from_handle(handle_input) if handle_input else ""
            file_texts = []
            for f in (uploaded_files or []):
                file_texts.append(enrich_from_file(f.read(), f.name, f.type))
            file_text = "\n\n".join(file_texts)
            st.session_state.context_text = build_context_text(url_text, file_text, handle_text)
            st.session_state.step = 4
            st.rerun()

# ── STEP 4: Clarification ─────────────────────────────────────────────────────
if st.session_state.step >= 4:
    with st.expander("Step 4 — A few quick questions", expanded=st.session_state.step == 4):
        agent = ClarificationAgent()
        question = agent.get_next_question(
            st.session_state.topic,
            st.session_state.persona,
            st.session_state.context_text,
            st.session_state.answers,
        )
        if question:
            answer = st.text_input(question, key=f"q_{question[:20]}")
            if st.button("Next →", key="clarify_next") and answer:
                for field in ["audience", "tone", "depth"]:
                    if field not in st.session_state.answers:
                        st.session_state.answers[field] = answer
                        break
                st.rerun()
        else:
            st.success("Brief complete. Ready to discover sources.")
            if st.button("Discover sources →", key="step4"):
                brief = agent.build_brief(
                    st.session_state.topic,
                    st.session_state.persona,
                    st.session_state.context_text,
                    st.session_state.answers,
                )
                st.session_state.brief = brief
                with st.spinner("Discovering sources..."):
                    raw = discover_sources(st.session_state.topic)
                    st.session_state.sources = score_sources(raw)
                st.session_state.step = 5
                st.rerun()

# ── STEP 5: Source curation ───────────────────────────────────────────────────
if st.session_state.step >= 5:
    with st.expander("Step 5 — Select your sources", expanded=st.session_state.step == 5):
        st.caption("Scored by recency · domain authority · relevance. Select sources you trust.")
        selected = []
        for src in st.session_state.sources:
            col1, col2 = st.columns([3, 1])
            with col1:
                checked = st.checkbox(f"**{src['title']}** — {src['domain']} ({src['date']})", key=src["url"])
                if checked:
                    selected.append(src)
            with col2:
                st.caption(f"Score: {src['overall_score']:.0%}")
        if st.button("Confirm sources →", key="step5") and selected:
            st.session_state.brief.selected_sources = selected
            st.session_state.step = 6
            st.rerun()

# ── STEP 6: Artifact selection ────────────────────────────────────────────────
if st.session_state.step >= 6:
    with st.expander("Step 6 — What do you want out?", expanded=st.session_state.step == 6):
        persona = st.session_state.persona
        if persona == "content_creator":
            options = ["content_brief", "social_draft", "captions", "hashtags", "calendar_entry"]
        else:
            options = ["research_brief", "competitive_summary", "opportunity_sizing", "prd_insights"]
        selected_artifacts = st.multiselect("Select artifacts to generate", options, default=[options[0]])
        if st.button("Run research agents →", key="step6") and selected_artifacts:
            st.session_state.brief.selected_artifacts = selected_artifacts
            st.session_state.step = 7
            st.rerun()

# ── STEP 7: Agent run + output ────────────────────────────────────────────────
if st.session_state.step >= 7:
    with st.expander("Step 7 — Research results", expanded=True):
        if "artifacts" not in st.session_state:
            with st.spinner("Agent crew working... (this takes 30–60 seconds)"):
                try:
                    crew = _load_crew(st.session_state.persona)
                    artifacts = crew.run(st.session_state.brief)
                    st.session_state.artifacts = artifacts
                except Exception as e:
                    st.error(f"Agent error: {e}")
                    st.stop()
        for artifact in st.session_state.get("artifacts", []):
            st.subheader(artifact["type"].replace("_", " ").title())
            exported = export_artifact(artifact)
            st.markdown(exported)
            st.download_button(
                f"Download {artifact['type']}",
                exported,
                file_name=f"{artifact['type']}.md",
                key=f"dl_{artifact['type']}",
            )
        if st.button("Start new research", key="restart"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
```

- [ ] **Step 2: Run the app locally**

```bash
streamlit run app.py
```
Expected: App opens at http://localhost:8501. Walk through all 7 steps using mock data.

- [ ] **Step 3: Commit**

```bash
git add app.py intake/
git commit -m "feat: full Streamlit UI — 7-step guided research flow"
```

---

## SQUAD 3 — Content Creator crew

> **Prerequisite:** Tasks 2–6 complete (LanceDB, LangFuse, BaseCrew available).

### Task 13: CC Retrieval agent

**Files:**
- Create: `crews/content_creator/__init__.py`
- Create: `crews/content_creator/retrieval_agent.py`
- Create: `tests/test_cc_retrieval.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cc_retrieval.py
from unittest.mock import patch, MagicMock
from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.base_crew import ResearchBrief

def test_cc_retrieval_returns_list(tmp_path):
    with patch("crews.content_creator.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.content_creator.retrieval_agent.VectorStore") as mock_vs:
        mock_scrape.return_value = [{"url": "https://a.com", "content": "travel content about Rajasthan", "title": "A", "domain": "a.com", "date": "2025-01-01"}]
        mock_vs.return_value.search.return_value = [{"text": "travel content", "metadata": {"source": "https://a.com"}}]
        agent = CCRetrievalAgent(db_path=str(tmp_path))
        brief = ResearchBrief(topic="sustainable travel Rajasthan", persona="content_creator", audience="millennials", tone="inspirational", depth="standard")
        results = agent.retrieve(brief, sources=[{"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01"}])
    assert isinstance(results, list)
    assert len(results) > 0

def test_cc_retrieval_prioritises_social_sources():
    agent = CCRetrievalAgent()
    assert "instagram" in agent.PRIORITY_SOURCES or "travel" in " ".join(agent.PRIORITY_SOURCES).lower()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_cc_retrieval.py -v
```
Expected: FAIL

- [ ] **Step 3: Create crews/content_creator/__init__.py**

```python
```

- [ ] **Step 4: Implement retrieval_agent.py**

```python
# crews/content_creator/retrieval_agent.py
from typing import List, Dict, Any
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore
from crews.base_crew import ResearchBrief

class CCRetrievalAgent:
    PRIORITY_SOURCES = ["instagram.com", "pinterest.com", "tripadvisor.com", "travelandleisure.com",
                        "lonelyplanet.com", "cntraveller.com", "theguardian.com/travel"]

    def __init__(self, db_path: str = ".lancedb_cc"):
        self.vector_store = VectorStore(db_path=db_path)

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        enriched = scrape_selected_sources(sources)
        texts, metadatas = [], []
        for src in enriched:
            if src["content"]:
                chunks = [src["content"][i:i+1000] for i in range(0, len(src["content"]), 1000)]
                for chunk in chunks[:5]:
                    texts.append(chunk)
                    metadatas.append({"source": src["url"], "title": src["title"], "domain": src["domain"], "date": src["date"]})
        if brief.context_text:
            texts.append(brief.context_text)
            metadatas.append({"source": "user_context", "title": "User context", "domain": "user", "date": "2026-01-01"})
        if texts:
            self.vector_store.add_texts(texts, metadatas, table_name="cc_research")
        query = f"{brief.topic} for {brief.audience} in {brief.tone} tone"
        return self.vector_store.search(query, table_name="cc_research", k=10)
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_cc_retrieval.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add crews/content_creator/ tests/test_cc_retrieval.py
git commit -m "feat: Content Creator retrieval agent — social and travel sources"
```

---

### Task 14: CC Analysis agent

**Files:**
- Create: `crews/content_creator/analysis_agent.py`
- Create: `tests/test_cc_analysis.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cc_analysis.py
from unittest.mock import patch, MagicMock
from crews.content_creator.analysis_agent import CCAnalysisAgent

def test_cc_analysis_returns_dict():
    with patch("crews.content_creator.analysis_agent.ChatAnthropic") as mock_llm:
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance
        mock_instance.invoke.return_value.content = '{"trends": ["eco tourism"], "hooks": ["Discover hidden Rajasthan"], "audience_signals": ["millennials prefer authentic"], "tone_notes": "inspirational"}'
        agent = CCAnalysisAgent()
        retrieved = [{"text": "Rajasthan eco tourism is growing among millennials", "metadata": {"source": "https://a.com"}}]
        result = agent.analyse(retrieved)
    assert "trends" in result
    assert "hooks" in result
    assert isinstance(result["hooks"], list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_cc_analysis.py -v
```
Expected: FAIL

- [ ] **Step 3: Implement analysis_agent.py**

```python
# crews/content_creator/analysis_agent.py
import json
from typing import List, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
import config

_SYSTEM = """You are a content strategy analyst. Given research excerpts, identify:
1. Trending angles and topics resonating with the audience
2. Compelling narrative hooks and story angles
3. Audience signals — what they care about, pain points, desires
4. Tone and style notes

Return valid JSON only with keys: trends, hooks, audience_signals, tone_notes, key_facts"""

class CCAnalysisAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model=config.ANALYSIS_MODEL, api_key=config.ANTHROPIC_API_KEY, temperature=0.4)

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        context = "\n\n".join(r["text"] for r in retrieved[:8])
        response = self.llm.invoke([
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Research excerpts:\n{context}\n\nAnalyse for content strategy:"),
        ])
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"trends": [], "hooks": [], "audience_signals": [], "tone_notes": response.content, "key_facts": []}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_cc_analysis.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crews/content_creator/analysis_agent.py tests/test_cc_analysis.py
git commit -m "feat: Content Creator analysis agent — trends, hooks, audience signals"
```

---

### Task 15: CC Output agent + templates

**Files:**
- Create: `crews/content_creator/output_agent.py`
- Create: `outputs/content_creator/templates.py`
- Create: `tests/test_cc_output.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cc_output.py
from unittest.mock import patch, MagicMock
from crews.content_creator.output_agent import CCOutputAgent

def test_cc_output_generates_selected_artifacts():
    with patch("crews.content_creator.output_agent.ChatAnthropic") as mock_llm:
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance
        mock_instance.invoke.return_value.content = "Generated content here"
        agent = CCOutputAgent()
        analysis = {"trends": ["eco travel"], "hooks": ["Hidden Rajasthan"], "audience_signals": ["millennials"], "tone_notes": "inspirational", "key_facts": []}
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["content_brief"])
    assert len(artifacts) == 1
    assert artifacts[0]["type"] == "content_brief"
    assert "content" in artifacts[0]

def test_cc_output_only_generates_selected():
    with patch("crews.content_creator.output_agent.ChatAnthropic") as mock_llm:
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance
        mock_instance.invoke.return_value.content = "Generated"
        agent = CCOutputAgent()
        analysis = {"trends": [], "hooks": [], "audience_signals": [], "tone_notes": "", "key_facts": []}
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["captions"])
    types = [a["type"] for a in artifacts]
    assert "captions" in types
    assert "content_brief" not in types
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_cc_output.py -v
```
Expected: FAIL

- [ ] **Step 3: Create outputs/content_creator/templates.py**

```python
# outputs/content_creator/templates.py

CONTENT_BRIEF_PROMPT = """Based on this analysis, write a structured content brief:
Analysis: {analysis}

Include:
- Topic overview (2-3 sentences)
- Key angles to cover (3-5 bullet points)
- Target audience profile
- Recommended tone and style
- 3 headline options
- Supporting facts and data points

Format as clean markdown."""

SOCIAL_DRAFT_PROMPT = """Write a social media post (LinkedIn/Instagram) based on this content analysis:
Analysis: {analysis}
Hook to use: {hook}
Tone: {tone}

Write 150-200 words. Start with the hook. Include a call to action."""

CAPTIONS_PROMPT = """Write 3 short social media captions (under 150 characters each) based on:
Analysis: {analysis}
Return as a numbered list."""

HASHTAGS_PROMPT = """Generate 20 relevant hashtags for this content:
Topic: {topic}
Analysis: {analysis}
Mix popular and niche hashtags. Return as space-separated #tags."""

CALENDAR_ENTRY_PROMPT = """Create a content calendar entry:
Analysis: {analysis}
Include: Best posting time, platform recommendation, content type, caption summary, hashtag count needed."""
```

- [ ] **Step 4: Implement output_agent.py**

```python
# crews/content_creator/output_agent.py
from typing import List, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from outputs.content_creator.templates import (
    CONTENT_BRIEF_PROMPT, SOCIAL_DRAFT_PROMPT, CAPTIONS_PROMPT, HASHTAGS_PROMPT, CALENDAR_ENTRY_PROMPT
)
import config

class CCOutputAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model=config.OUTPUT_MODEL, api_key=config.ANTHROPIC_API_KEY, temperature=0.6)

    def _generate(self, prompt: str) -> str:
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def generate_artifacts(self, analysis: Dict[str, Any], selected_artifacts: List[str]) -> List[Dict[str, Any]]:
        hook = analysis.get("hooks", [""])[0] if analysis.get("hooks") else ""
        tone = analysis.get("tone_notes", "informative")
        artifacts = []
        generators = {
            "content_brief": lambda: self._generate(CONTENT_BRIEF_PROMPT.format(analysis=analysis)),
            "social_draft": lambda: self._generate(SOCIAL_DRAFT_PROMPT.format(analysis=analysis, hook=hook, tone=tone)),
            "captions": lambda: self._generate(CAPTIONS_PROMPT.format(analysis=analysis)),
            "hashtags": lambda: self._generate(HASHTAGS_PROMPT.format(topic=analysis.get("trends", [""])[0], analysis=analysis)),
            "calendar_entry": lambda: self._generate(CALENDAR_ENTRY_PROMPT.format(analysis=analysis)),
        }
        for artifact_type in selected_artifacts:
            if artifact_type in generators:
                content = generators[artifact_type]()
                artifacts.append({"type": artifact_type, "content": content, "citations": []})
        return artifacts
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_cc_output.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add crews/content_creator/output_agent.py outputs/content_creator/ tests/test_cc_output.py
git commit -m "feat: Content Creator output agent — all 5 artifact types"
```

---

### Task 16: CC end-to-end smoke test

**Files:**
- Create: `tests/test_cc_e2e.py`

- [ ] **Step 1: Write smoke test**

```python
# tests/test_cc_e2e.py
from unittest.mock import patch, MagicMock
from crews.base_crew import ResearchBrief
from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.content_creator.analysis_agent import CCAnalysisAgent
from crews.content_creator.output_agent import CCOutputAgent

def test_cc_crew_full_pipeline(tmp_path):
    brief = ResearchBrief(
        topic="sustainable travel Rajasthan",
        persona="content_creator",
        audience="millennials",
        tone="inspirational",
        depth="standard",
        selected_sources=[{"url": "https://a.com", "title": "A", "domain": "a.com", "date": "2025-01-01"}],
        selected_artifacts=["content_brief", "captions"],
    )
    with patch("crews.content_creator.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.content_creator.retrieval_agent.VectorStore") as mock_vs, \
         patch("crews.content_creator.analysis_agent.ChatAnthropic") as mock_analysis_llm, \
         patch("crews.content_creator.output_agent.ChatAnthropic") as mock_output_llm:

        mock_scrape.return_value = [{"url": "https://a.com", "content": "Rajasthan eco travel", "title": "A", "domain": "a.com", "date": "2025-01-01"}]
        mock_vs.return_value.search.return_value = [{"text": "eco travel content", "metadata": {"source": "a.com"}}]
        mock_analysis_llm.return_value.invoke.return_value.content = '{"trends": ["eco tourism"], "hooks": ["Discover Rajasthan"], "audience_signals": ["millennials"], "tone_notes": "inspirational", "key_facts": []}'
        mock_output_llm.return_value.invoke.return_value.content = "Generated content"

        retrieval = CCRetrievalAgent(db_path=str(tmp_path))
        analysis = CCAnalysisAgent()
        output = CCOutputAgent()

        retrieved = retrieval.retrieve(brief, brief.selected_sources)
        analysed = analysis.analyse(retrieved)
        artifacts = output.generate_artifacts(analysed, brief.selected_artifacts)

    assert len(artifacts) == 2
    types = [a["type"] for a in artifacts]
    assert "content_brief" in types
    assert "captions" in types
```

- [ ] **Step 2: Run smoke test**

```bash
pytest tests/test_cc_e2e.py -v
```
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_cc_e2e.py
git commit -m "test: Content Creator crew end-to-end smoke test"
```

---

## SQUAD 4 — Product Manager crew

> **Prerequisite:** Tasks 2–6 complete.

### Task 17: PM Retrieval agent

**Files:**
- Create: `crews/product_manager/__init__.py`
- Create: `crews/product_manager/retrieval_agent.py`
- Create: `tests/test_pm_retrieval.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_pm_retrieval.py
from unittest.mock import patch, MagicMock
from crews.product_manager.retrieval_agent import PMRetrievalAgent
from crews.base_crew import ResearchBrief

def test_pm_retrieval_returns_list(tmp_path):
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs:
        mock_scrape.return_value = [{"url": "https://mckinsey.com/a", "content": "travel market growing 20% YoY", "title": "M", "domain": "mckinsey.com", "date": "2025-01-01"}]
        mock_vs.return_value.search.return_value = [{"text": "market data", "metadata": {"source": "mckinsey.com"}}]
        agent = PMRetrievalAgent(db_path=str(tmp_path))
        brief = ResearchBrief(topic="sustainable travel market India", persona="product_manager", audience="investors", tone="analytical", depth="deep")
        results = agent.retrieve(brief, sources=[{"url": "https://mckinsey.com/a", "title": "M", "domain": "mckinsey.com", "date": "2025-01-01"}])
    assert isinstance(results, list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_pm_retrieval.py -v
```
Expected: FAIL

- [ ] **Step 3: Create crews/product_manager/__init__.py**

```python
```

- [ ] **Step 4: Implement retrieval_agent.py**

```python
# crews/product_manager/retrieval_agent.py
from typing import List, Dict, Any
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore
from crews.base_crew import ResearchBrief

class PMRetrievalAgent:
    PRIORITY_SOURCES = ["mckinsey.com", "hbr.org", "statista.com", "bloomberg.com",
                        "reuters.com", "crunchbase.com", "techcrunch.com", "forrester.com"]

    def __init__(self, db_path: str = ".lancedb_pm"):
        self.vector_store = VectorStore(db_path=db_path)

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        enriched = scrape_selected_sources(sources)
        texts, metadatas = [], []
        for src in enriched:
            if src["content"]:
                chunks = [src["content"][i:i+1000] for i in range(0, len(src["content"]), 1000)]
                for chunk in chunks[:5]:
                    texts.append(chunk)
                    metadatas.append({"source": src["url"], "title": src["title"], "domain": src["domain"], "date": src["date"]})
        if brief.context_text:
            texts.append(brief.context_text)
            metadatas.append({"source": "user_context", "title": "User context", "domain": "user", "date": "2026-01-01"})
        if texts:
            self.vector_store.add_texts(texts, metadatas, table_name="pm_research")
        query = f"{brief.topic} market size competition user pain points data"
        return self.vector_store.search(query, table_name="pm_research", k=10)
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/test_pm_retrieval.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add crews/product_manager/ tests/test_pm_retrieval.py
git commit -m "feat: Product Manager retrieval agent — market and industry sources"
```

---

### Task 18: PM Analysis + Output agents

**Files:**
- Create: `crews/product_manager/analysis_agent.py`
- Create: `crews/product_manager/output_agent.py`
- Create: `outputs/product_manager/templates.py`
- Create: `tests/test_pm_agents.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_pm_agents.py
from unittest.mock import patch, MagicMock
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent

def test_pm_analysis_returns_dict():
    with patch("crews.product_manager.analysis_agent.ChatAnthropic") as mock_llm:
        mock_llm.return_value.invoke.return_value.content = '{"market_size": "large", "competitors": ["A", "B"], "user_pain_points": ["cost"], "opportunity": "high", "contradictions": []}'
        agent = PMAnalysisAgent()
        result = agent.analyse([{"text": "market data here", "metadata": {}}])
    assert "market_size" in result
    assert "competitors" in result

def test_pm_output_generates_selected_artifacts():
    with patch("crews.product_manager.output_agent.ChatAnthropic") as mock_llm:
        mock_llm.return_value.invoke.return_value.content = "Generated PM content"
        agent = PMOutputAgent()
        analysis = {"market_size": "large", "competitors": ["A"], "user_pain_points": ["cost"], "opportunity": "high", "contradictions": []}
        artifacts = agent.generate_artifacts(analysis, selected_artifacts=["research_brief"])
    assert len(artifacts) == 1
    assert artifacts[0]["type"] == "research_brief"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_pm_agents.py -v
```
Expected: FAIL

- [ ] **Step 3: Create outputs/product_manager/templates.py**

```python
# outputs/product_manager/templates.py

RESEARCH_BRIEF_PROMPT = """Write a structured research brief for a product manager based on:
Analysis: {analysis}

Include:
- Executive summary (3 sentences)
- Key findings (5 bullet points with data)
- Market landscape
- Identified gaps and opportunities
- Recommended next steps

Format as clean markdown with headers."""

COMPETITIVE_SUMMARY_PROMPT = """Write a competitive landscape summary based on:
Analysis: {analysis}

Include for each competitor: positioning, strengths, weaknesses, market share if known.
Format as a markdown table followed by 3 strategic insights."""

OPPORTUNITY_SIZING_PROMPT = """Write an opportunity sizing analysis based on:
Analysis: {analysis}

Include: TAM/SAM/SOM estimates (with caveats), growth rate, key assumptions, confidence level."""

PRD_INSIGHTS_PROMPT = """Extract PRD-ready insights from:
Analysis: {analysis}

Format as:
## User Problems
- Problem: [description] | Evidence: [source]

## Opportunity Statement
[One paragraph]

## Success Metrics
- [Metric]: [target]"""
```

- [ ] **Step 4: Implement analysis_agent.py**

```python
# crews/product_manager/analysis_agent.py
import json
from typing import List, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
import config

_SYSTEM = """You are a market research analyst. Given research excerpts, identify:
1. Market size and growth signals
2. Key competitors and their positioning
3. User pain points supported by evidence
4. Opportunity areas and gaps
5. Any contradictions or conflicting data across sources

Return valid JSON only with keys: market_size, competitors, user_pain_points, opportunity, contradictions, key_data_points"""

class PMAnalysisAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model=config.ANALYSIS_MODEL, api_key=config.ANTHROPIC_API_KEY, temperature=0.2)

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        context = "\n\n".join(r["text"] for r in retrieved[:8])
        response = self.llm.invoke([
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Research excerpts:\n{context}\n\nAnalyse for product strategy:"),
        ])
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"market_size": "unknown", "competitors": [], "user_pain_points": [], "opportunity": response.content, "contradictions": [], "key_data_points": []}
```

- [ ] **Step 5: Implement output_agent.py**

```python
# crews/product_manager/output_agent.py
from typing import List, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage
from outputs.product_manager.templates import (
    RESEARCH_BRIEF_PROMPT, COMPETITIVE_SUMMARY_PROMPT, OPPORTUNITY_SIZING_PROMPT, PRD_INSIGHTS_PROMPT
)
import config

class PMOutputAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model=config.OUTPUT_MODEL, api_key=config.ANTHROPIC_API_KEY, temperature=0.3)

    def _generate(self, prompt: str) -> str:
        return self.llm.invoke([HumanMessage(content=prompt)]).content

    def generate_artifacts(self, analysis: Dict[str, Any], selected_artifacts: List[str]) -> List[Dict[str, Any]]:
        artifacts = []
        generators = {
            "research_brief": lambda: self._generate(RESEARCH_BRIEF_PROMPT.format(analysis=analysis)),
            "competitive_summary": lambda: self._generate(COMPETITIVE_SUMMARY_PROMPT.format(analysis=analysis)),
            "opportunity_sizing": lambda: self._generate(OPPORTUNITY_SIZING_PROMPT.format(analysis=analysis)),
            "prd_insights": lambda: self._generate(PRD_INSIGHTS_PROMPT.format(analysis=analysis)),
        }
        for artifact_type in selected_artifacts:
            if artifact_type in generators:
                artifacts.append({"type": artifact_type, "content": generators[artifact_type](), "citations": []})
        return artifacts
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_pm_agents.py -v
```
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add crews/product_manager/analysis_agent.py crews/product_manager/output_agent.py outputs/product_manager/ tests/test_pm_agents.py
git commit -m "feat: Product Manager analysis + output agents — all 4 artifact types"
```

---

### Task 19: PM end-to-end smoke test

**Files:**
- Create: `tests/test_pm_e2e.py`

- [ ] **Step 1: Write smoke test**

```python
# tests/test_pm_e2e.py
from unittest.mock import patch, MagicMock
from crews.base_crew import ResearchBrief
from crews.product_manager.retrieval_agent import PMRetrievalAgent
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent

def test_pm_crew_full_pipeline(tmp_path):
    brief = ResearchBrief(
        topic="sustainable travel market India",
        persona="product_manager",
        audience="investors",
        tone="analytical",
        depth="deep",
        selected_sources=[{"url": "https://mckinsey.com/a", "title": "M", "domain": "mckinsey.com", "date": "2025-01-01"}],
        selected_artifacts=["research_brief", "competitive_summary"],
    )
    with patch("crews.product_manager.retrieval_agent.scrape_selected_sources") as mock_scrape, \
         patch("crews.product_manager.retrieval_agent.VectorStore") as mock_vs, \
         patch("crews.product_manager.analysis_agent.ChatAnthropic") as mock_analysis, \
         patch("crews.product_manager.output_agent.ChatAnthropic") as mock_output:

        mock_scrape.return_value = [{"url": "https://mckinsey.com/a", "content": "market growing", "title": "M", "domain": "mckinsey.com", "date": "2025-01-01"}]
        mock_vs.return_value.search.return_value = [{"text": "market data", "metadata": {}}]
        mock_analysis.return_value.invoke.return_value.content = '{"market_size": "large", "competitors": ["A"], "user_pain_points": ["cost"], "opportunity": "high", "contradictions": [], "key_data_points": []}'
        mock_output.return_value.invoke.return_value.content = "Generated PM content"

        retrieved = PMRetrievalAgent(db_path=str(tmp_path)).retrieve(brief, brief.selected_sources)
        analysed = PMAnalysisAgent().analyse(retrieved)
        artifacts = PMOutputAgent().generate_artifacts(analysed, brief.selected_artifacts)

    assert len(artifacts) == 2
    types = [a["type"] for a in artifacts]
    assert "research_brief" in types
    assert "competitive_summary" in types
```

- [ ] **Step 2: Run smoke test**

```bash
pytest tests/test_pm_e2e.py -v
```
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_pm_e2e.py
git commit -m "test: Product Manager crew end-to-end smoke test"
```

---

## ALL SQUADS — Integration + Demo prep

### Task 20: Full integration + Loom prep

**Files:**
- Verify: `app.py` wires all crews correctly
- Create: `tests/test_integration.py`

- [ ] **Step 1: Run full test suite**

```bash
pytest tests/ -v
```
Expected: All tests PASS

- [ ] **Step 2: Run the app end-to-end with real API keys**

```bash
streamlit run app.py
```
Walk through the full flow:
1. Select Content Creator
2. Topic: "Sustainable travel in Rajasthan for millennial travellers"
3. Upload BharatDesha URL: https://bharatdesha.com
4. Complete clarification questions
5. Select 3-5 sources from the surfaced list
6. Select artifacts: content_brief + captions + hashtags
7. Verify artifacts render correctly with citations

- [ ] **Step 3: Walk through PM persona**

Restart app. Select Product Manager. Same topic. Select: research_brief + competitive_summary. Verify output is distinctly different from CC output.

- [ ] **Step 4: Check LangFuse dashboard**

Open https://cloud.langfuse.com — verify traces are appearing for both crew runs. Screenshot for the Loom.

- [ ] **Step 5: Fix any integration issues**

Common issues:
- Import errors → check `__init__.py` files exist in all packages
- LanceDB table name conflicts between CC and PM crews → each uses its own db_path
- LLM rate limits → add `time.sleep(1)` between agent calls if needed

- [ ] **Step 6: Record Loom (5 minutes)**

Follow the demo arc from the pitch deck:
- 0:00–0:30 Problem statement
- 0:30–1:00 Persona + topic + BharatDesha URL
- 1:00–1:45 Clarification + source curation with confidence scores
- 1:45–2:15 Artifact selection + agents running
- 2:15–3:30 Output reveal — content brief + captions + hashtags
- 3:30–4:15 Switch to PM persona, same topic, different output
- 4:15–5:00 Architecture + closing line: "We built a platform, not a demo"

- [ ] **Step 7: Final commit**

```bash
git add .
git commit -m "feat: full integration — Multi-Agent Deep Researcher v1.0"
```

---

## SQUAD 2 — Production deployment setup

### Task 21: Dockerfile + Streamlit Cloud deployment

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.dockerignore`
- Create: `.streamlit/config.toml`

- [ ] **Step 1: Create .streamlit/config.toml**

```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

- [ ] **Step 2: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for BeautifulSoup + PDF parsing
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory for LanceDB in production
RUN mkdir -p /data/lancedb

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

- [ ] **Step 3: Create docker-compose.yml**

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - APP_ENV=local
    env_file:
      - .env.local
    volumes:
      - lancedb_data:/data/lancedb
    restart: unless-stopped

volumes:
  lancedb_data:
```

- [ ] **Step 4: Create .dockerignore**

```
.env.local
.env.production
.lancedb_local/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
.git/
tests/
docs/
.superpowers/
```

- [ ] **Step 5: Test Docker build locally**

```bash
docker compose build
docker compose up
```
Open http://localhost:8501 — verify app loads correctly with local env.

- [ ] **Step 6: Deploy to Streamlit Community Cloud**

1. Push repo to GitHub (ensure `.env.local` and `.env.production` are gitignored ✓)
2. Go to https://share.streamlit.io → New app → select repo → set `app.py` as entry point
3. In Streamlit Cloud → Settings → Secrets, add all keys from `.env.production.example`:
   ```
   APP_ENV = "production"
   OPENAI_API_KEY = "sk-..."
   ANTHROPIC_API_KEY = "sk-ant-..."
   TAVILY_API_KEY = "tvly-..."
   LANGFUSE_SECRET_KEY = "sk-lf-..."
   LANGFUSE_PUBLIC_KEY = "pk-lf-..."
   LANGFUSE_HOST = "https://cloud.langfuse.com"
   LANCEDB_PATH = "/data/lancedb"
   ```
4. Deploy → copy the live URL for the Loom recording

- [ ] **Step 7: Verify production deployment**

Open the Streamlit Cloud URL. Walk through the full 7-step flow. Confirm LangFuse traces appear at https://cloud.langfuse.com.

- [ ] **Step 8: Commit**

```bash
git add Dockerfile docker-compose.yml .dockerignore .streamlit/
git commit -m "feat: production deployment — Docker + Streamlit Cloud"
```

---

## Phase 2 — FastAPI migration (post-hackathon, BharatDesha production)

> **Not a hackathon task.** Documented here as the specced next phase so the architecture is already designed for it. Estimated effort: one afternoon (~4 hours).

### What changes

**New file: `api.py`** (~100 lines)

```python
from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from crews.base_crew import ResearchBrief, CrewOutput
from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.content_creator.analysis_agent import CCAnalysisAgent
from crews.content_creator.output_agent import CCOutputAgent
from crews.product_manager.retrieval_agent import PMRetrievalAgent
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent
from observability.langfuse_client import get_langfuse_handler
import uuid

app = FastAPI(title="Deep Researcher API", version="2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def _get_crew(persona: str):
    if persona == "content_creator":
        return CCRetrievalAgent(), CCAnalysisAgent(), CCOutputAgent()
    return PMRetrievalAgent(), PMAnalysisAgent(), PMOutputAgent()

@app.post("/research", response_model=CrewOutput)
async def run_research(brief: ResearchBrief):
    retrieval, analysis, output = _get_crew(brief.persona)
    retrieved = retrieval.retrieve(brief, brief.selected_sources)
    analysed = analysis.analyse(retrieved)
    artifacts = output.generate_artifacts(analysed, brief.selected_artifacts)
    return CrewOutput(artifacts=artifacts, trace_id=str(uuid.uuid4()))

@app.get("/health")
async def health():
    return {"status": "ok", "env": config.APP_ENV}
```

**`app.py` becomes a thin client** — replace direct crew calls with:
```python
import requests
response = requests.post("http://localhost:8000/research", json=brief.__dict__)
artifacts = response.json()["artifacts"]
```

**`Dockerfile` CMD** — one line change:
```dockerfile
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**New file: `docker-compose.production.yml`** — separate frontend and backend containers:
```yaml
version: "3.8"
services:
  api:
    build: .
    ports: ["8000:8000"]
    env_file: .env.production
    volumes: [lancedb_data:/data/lancedb]
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports: ["8501:8501"]
    environment:
      - API_URL=http://api:8000
    depends_on: [api]
volumes:
  lancedb_data:
```

### What does not change
- All agent files (`crews/`, `infrastructure/`, `source_engine/`, `observability/`) — zero changes
- All tests — zero changes
- `config.py` — zero changes
- `BaseCrew` contract — zero changes

### Phase 3 — Adding a new persona (e.g. BharatDesha)
1. Create `crews/bharatdesha/` with `retrieval_agent.py`, `analysis_agent.py`, `output_agent.py`
2. Subclass `BaseCrew` in each
3. Add `outputs/bharatdesha/templates.py`
4. Register in `api.py` `_get_crew()` — one `elif` line
5. Add persona option to `app.py` UI — one line

**Total effort per new persona: ~3 hours.**
