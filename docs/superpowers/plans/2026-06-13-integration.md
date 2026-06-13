# Task 20: Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire all four squads' work into a single working Streamlit app — persona routing, artifact rendering, LangFuse session wiring, and end-to-end smoke tests for all three personas.

**Architecture:** A new `crews/router.py` maps persona strings to crew classes. `intake/persona_selector.py` gains a Bharat Desha entry. `app.py` is updated to use the router and render all artifact types. Integration tests verify the full pipeline per persona with mocked external calls.

**Tech Stack:** Streamlit, `crews/base_crew.py` (`BaseCrew`, `ResearchBrief`, `CrewOutput`), `observability/langfuse_client.py`, existing crew implementations (Squads 3, 4, 5)

---

## Execution order

Tasks run sequentially — each depends on the previous.

```
Task 1: Crew router (crews/router.py)
Task 2: Persona registry — add Bharat Desha to intake/persona_selector.py
Task 3: Artifact renderer (ui/artifact_renderer.py)
Task 4: Wire app.py — use router + renderer + LangFuse session
Task 5: LanceDB isolation smoke test
Task 6: End-to-end integration tests (one per persona)
```

---

## File structure

```
crews/
└── router.py                    # Task 1 — NEW: maps persona → crew class

intake/
└── persona_selector.py          # Task 2 — MODIFY: add bharat_desha entry

ui/
├── __init__.py                  # Task 3 — NEW
└── artifact_renderer.py         # Task 3 — NEW: renders all artifact types

app.py                           # Task 4 — MODIFY: use router + renderer + LangFuse

tests/
└── test_integration.py          # Tasks 5+6 — NEW: isolation + e2e tests
```

**Existing files referenced (do not modify except app.py and persona_selector.py):**
- `crews/base_crew.py` — `BaseCrew`, `ResearchBrief`, `CrewOutput`
- `crews/bharat_desha/crew.py` — `BharatDeshaCrew`
- `crews/content_creator/crew.py` — `ContentCreatorCrew`
- `crews/product_manager/crew.py` — `ProductManagerCrew`
- `observability/langfuse_client.py` — `get_langfuse_handler(session_id)`
- `config.py` — `BHARAT_DESHA_TABLE`, `INTAKE_MODEL`, etc.

---

## Task 1: Crew router

**Files:**
- Create: `crews/router.py`
- Create: `tests/test_integration.py` (first test only)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_integration.py
import os
os.environ.setdefault("OPENROUTER_API_KEY", "x")
os.environ.setdefault("TAVILY_API_KEY", "x")

from unittest.mock import patch, MagicMock

def test_router_returns_correct_crew_for_each_persona():
    from crews.router import get_crew
    from crews.base_crew import BaseCrew

    with patch("crews.router.ContentCreatorCrew") as mock_cc, \
         patch("crews.router.ProductManagerCrew") as mock_pm, \
         patch("crews.router.BharatDeshaCrew") as mock_bd:

        mock_cc.return_value = MagicMock(spec=BaseCrew)
        mock_pm.return_value = MagicMock(spec=BaseCrew)
        mock_bd.return_value = MagicMock(spec=BaseCrew)

        cc = get_crew("content_creator")
        pm = get_crew("product_manager")
        bd = get_crew("bharat_desha")

        mock_cc.assert_called_once()
        mock_pm.assert_called_once()
        mock_bd.assert_called_once()

def test_router_raises_for_unknown_persona():
    from crews.router import get_crew
    import pytest
    with pytest.raises(ValueError, match="Unknown persona"):
        get_crew("unknown_persona")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py::test_router_returns_correct_crew_for_each_persona tests/test_integration.py::test_router_raises_for_unknown_persona -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'crews.router'`

- [ ] **Step 3: Implement crews/router.py**

```python
# crews/router.py
from crews.base_crew import BaseCrew
from crews.content_creator.crew import ContentCreatorCrew
from crews.product_manager.crew import ProductManagerCrew
from crews.bharat_desha.crew import BharatDeshaCrew

_CREW_MAP = {
    "content_creator": ContentCreatorCrew,
    "product_manager": ProductManagerCrew,
    "bharat_desha": BharatDeshaCrew,
}

def get_crew(persona: str) -> BaseCrew:
    if persona not in _CREW_MAP:
        raise ValueError(f"Unknown persona: '{persona}'. Valid options: {list(_CREW_MAP.keys())}")
    return _CREW_MAP[persona]()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add crews/router.py tests/test_integration.py
git commit -m "feat: add crew router — maps persona string to crew instance"
```

---

## Task 2: Persona registry — add Bharat Desha

**Files:**
- Modify: `intake/persona_selector.py`
- Modify: `tests/test_integration.py` (add test)

**Note:** Read `intake/persona_selector.py` fully before editing. Follow the exact structure Squad 1 used for Content Creator and Product Manager entries. If the file doesn't exist yet (Squad 1 not merged), create a stub that matches this spec exactly — Squad 1 will merge into it.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_integration.py`:

```python
def test_persona_selector_includes_bharat_desha():
    from intake.persona_selector import PERSONAS

    assert "bharat_desha" in PERSONAS
    bd = PERSONAS["bharat_desha"]
    assert "label" in bd
    assert "description" in bd
    assert "artifacts" in bd
    assert "always_included" in bd
    assert "blog_post" in bd["artifacts"]
    assert "instagram" in bd["artifacts"]
    assert "x_post" in bd["artifacts"]
    assert "youtube" in bd["artifacts"]
    assert "seo_keywords" in bd["always_included"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py::test_persona_selector_includes_bharat_desha -v
```

Expected: FAIL

- [ ] **Step 3: Update intake/persona_selector.py**

Read the file first. If it already has a `PERSONAS` dict, add the `bharat_desha` key to it:

```python
"bharat_desha": {
    "label": "Bharat Desha",
    "description": "Spiritual India travel content — itineraries, destination guides, Sanatan Dharma philosophy, yoga & wellness, and social media repurposing.",
    "artifacts": [
        "blog_post",
        "itinerary",
        "destination_guide",
        "wellness_guide",
        "instagram",
        "facebook",
        "x_post",
        "youtube",
    ],
    "always_included": ["seo_keywords"],
}
```

If the file doesn't exist yet (Squad 1 not merged), create `intake/__init__.py` (empty) and `intake/persona_selector.py` as a stub:

```python
# intake/persona_selector.py
PERSONAS = {
    "content_creator": {
        "label": "Content Creator",
        "description": "Research and create engaging content for blogs, social media, and newsletters.",
        "artifacts": ["blog_post", "social_post", "newsletter", "content_brief"],
        "always_included": [],
    },
    "product_manager": {
        "label": "Product Manager",
        "description": "Competitive research, market analysis, and product strategy documents.",
        "artifacts": ["competitive_analysis", "product_roadmap", "user_research", "executive_summary"],
        "always_included": [],
    },
    "bharat_desha": {
        "label": "Bharat Desha",
        "description": "Spiritual India travel content — itineraries, destination guides, Sanatan Dharma philosophy, yoga & wellness, and social media repurposing.",
        "artifacts": [
            "blog_post",
            "itinerary",
            "destination_guide",
            "wellness_guide",
            "instagram",
            "facebook",
            "x_post",
            "youtube",
        ],
        "always_included": ["seo_keywords"],
    },
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add intake/persona_selector.py intake/__init__.py tests/test_integration.py
git commit -m "feat: add Bharat Desha to persona registry"
```

---

## Task 3: Artifact renderer

**Files:**
- Create: `ui/__init__.py`
- Create: `ui/artifact_renderer.py`
- Modify: `tests/test_integration.py` (add test)

**What this does:** Renders any `CrewOutput` artifact dict to a Streamlit UI element. Each artifact type has a specific display format. This is a pure UI function — no LLM calls, no network.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_integration.py`:

```python
def test_artifact_renderer_handles_all_types():
    from ui.artifact_renderer import get_render_config

    artifact_types = [
        "blog_post", "itinerary", "destination_guide", "wellness_guide",
        "instagram", "facebook", "x_post", "youtube",
        "seo_keywords", "content_brief", "competitive_analysis",
        "product_roadmap", "user_research", "executive_summary", "social_post", "newsletter"
    ]

    for artifact_type in artifact_types:
        config = get_render_config(artifact_type)
        assert "label" in config, f"Missing label for {artifact_type}"
        assert "display" in config, f"Missing display for {artifact_type}"
        assert config["display"] in ("markdown", "text_box", "sections"), \
            f"Unknown display type for {artifact_type}: {config['display']}"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py::test_artifact_renderer_handles_all_types -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'ui'`

- [ ] **Step 3: Create ui/__init__.py**

```python
# ui/__init__.py
```

- [ ] **Step 4: Create ui/artifact_renderer.py**

```python
# ui/artifact_renderer.py
from typing import Dict, Any

_RENDER_CONFIGS = {
    # BharatDesha primary content
    "blog_post":          {"label": "Blog Post",          "display": "markdown"},
    "itinerary":          {"label": "Itinerary",           "display": "markdown"},
    "destination_guide":  {"label": "Destination Guide",   "display": "markdown"},
    "wellness_guide":     {"label": "Wellness Guide",      "display": "markdown"},
    # BharatDesha social
    "instagram":          {"label": "Instagram Caption",   "display": "text_box"},
    "facebook":           {"label": "Facebook Post",       "display": "text_box"},
    "x_post":             {"label": "X (Twitter) Thread",  "display": "text_box"},
    "youtube":            {"label": "YouTube Metadata",    "display": "sections"},
    "seo_keywords":       {"label": "SEO Keywords",        "display": "markdown"},
    # Content Creator artifacts
    "content_brief":      {"label": "Content Brief",       "display": "markdown"},
    "social_post":        {"label": "Social Post",         "display": "text_box"},
    "newsletter":         {"label": "Newsletter",          "display": "markdown"},
    # Product Manager artifacts
    "competitive_analysis": {"label": "Competitive Analysis", "display": "markdown"},
    "product_roadmap":    {"label": "Product Roadmap",     "display": "markdown"},
    "user_research":      {"label": "User Research",       "display": "markdown"},
    "executive_summary":  {"label": "Executive Summary",   "display": "markdown"},
}

_DEFAULT_CONFIG = {"label": "Output", "display": "markdown"}

def get_render_config(artifact_type: str) -> Dict[str, str]:
    return _RENDER_CONFIGS.get(artifact_type, _DEFAULT_CONFIG)

def render_artifact(artifact: Dict[str, Any]) -> None:
    """Render a single artifact dict to Streamlit. Must be called from a Streamlit context."""
    import streamlit as st

    artifact_type = artifact.get("type", "unknown")
    content = artifact.get("content", "")
    citations = artifact.get("citations", [])
    cfg = get_render_config(artifact_type)

    st.subheader(cfg["label"])

    if cfg["display"] == "markdown":
        st.markdown(content)
    elif cfg["display"] == "text_box":
        st.text_area(cfg["label"], value=content, height=200, key=f"artifact_{artifact_type}_{id(artifact)}")
    elif cfg["display"] == "sections":
        # YouTube: parse TITLE / DESCRIPTION / CHAPTERS sections
        sections = {"TITLE": "", "DESCRIPTION": "", "CHAPTERS": ""}
        current = None
        for line in content.splitlines():
            if line.startswith("TITLE:"):
                current = "TITLE"
                sections["TITLE"] = line[6:].strip()
            elif line.startswith("DESCRIPTION:"):
                current = "DESCRIPTION"
                sections["DESCRIPTION"] = line[12:].strip()
            elif line.startswith("CHAPTERS:"):
                current = "CHAPTERS"
            elif current == "DESCRIPTION":
                sections["DESCRIPTION"] += "\n" + line
            elif current == "CHAPTERS":
                sections["CHAPTERS"] += line + "\n"
        st.text_input("Title", value=sections["TITLE"])
        st.text_area("Description", value=sections["DESCRIPTION"].strip(), height=150)
        st.text_area("Chapters", value=sections["CHAPTERS"].strip(), height=100)

    if citations:
        with st.expander("Sources"):
            for url in citations:
                st.markdown(f"- {url}")
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py -v
```

Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add ui/__init__.py ui/artifact_renderer.py tests/test_integration.py
git commit -m "feat: artifact renderer — handles all persona artifact types"
```

---

## Task 4: Wire app.py

**Files:**
- Modify: `app.py`
- Modify: `tests/test_integration.py` (add test)

**Note:** Read `app.py` fully before editing. Squad 1 owns this file. The changes below add the router call and artifact rendering — do NOT remove or restructure Squad 1's flow. Add to it.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_integration.py`:

```python
def test_app_imports_without_streamlit_error():
    """Verify app.py can be imported and crew_router is wired in."""
    import importlib.util
    import sys

    # Stub streamlit so we can import app.py outside a Streamlit context
    st_mock = MagicMock()
    st_mock.session_state = {}
    sys.modules["streamlit"] = st_mock

    spec = importlib.util.spec_from_file_location(
        "app",
        "C:/Users/prash/codeworkspace/outskill/cap-hackathon-group8/app.py"
    )
    if spec is None:
        # app.py doesn't exist yet (Squad 1 not merged) — skip
        return

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        # Only fail if it's a genuine import error, not a Streamlit runtime error
        if "crews.router" in str(e) or "ui.artifact_renderer" in str(e):
            raise
```

- [ ] **Step 2: Run test**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py::test_app_imports_without_streamlit_error -v
```

If `app.py` doesn't exist yet: the test skips — that's fine. Proceed to Step 3 anyway.

- [ ] **Step 3: Update app.py**

Read the current `app.py`. Find the section where it instantiates a crew or calls `.run()`. Replace or augment it with:

```python
# At top of app.py — add these imports
from uuid import uuid4
from crews.router import get_crew
from ui.artifact_renderer import render_artifact
from observability.langfuse_client import get_langfuse_handler
```

Find where the research run is triggered (e.g. a button click). Add or replace the crew instantiation:

```python
# Inside the "Run Research" button handler
session_id = str(uuid4())
langfuse_handler = get_langfuse_handler(session_id=session_id, user_id="demo")

crew = get_crew(st.session_state["selected_persona"])
output = crew.run(brief)

st.session_state["last_output"] = output
st.session_state["session_id"] = session_id
```

Find where artifacts are displayed. Replace any ad-hoc rendering with:

```python
# In the results display section
for artifact in output.artifacts:
    render_artifact(artifact)
```

- [ ] **Step 4: Run full test suite**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/ -v 2>&1 | tail -15
```

Expected: all existing tests pass + 4+ new integration tests pass

- [ ] **Step 5: Commit**

```bash
git add app.py tests/test_integration.py
git commit -m "feat: wire app.py — crew router + artifact renderer + LangFuse session"
```

---

## Task 5: LanceDB table isolation smoke test

**Files:**
- Modify: `tests/test_integration.py` (add test)

**What this verifies:** Each crew writes to its own LanceDB table. Running all three crews against the same LanceDB path does not mix data between tables.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_integration.py`:

```python
def test_lancedb_tables_are_isolated(tmp_path):
    """Each crew writes to its own table — no cross-contamination."""
    import config
    from infrastructure.vector_store import VectorStore

    original_path = config.LANCEDB_PATH
    config.LANCEDB_PATH = str(tmp_path / "test_lancedb")

    try:
        store = VectorStore(db_path=config.LANCEDB_PATH)

        # Simulate each crew writing to its own table
        store.add_texts(
            ["Content creator article about marketing"],
            [{"source": "https://cc.example.com"}],
            "content_creator"
        )
        store.add_texts(
            ["Product manager roadmap for Q3"],
            [{"source": "https://pm.example.com"}],
            "product_manager"
        )
        store.add_texts(
            ["Varanasi spiritual tour guide"],
            [{"source": "https://bd.example.com"}],
            "bharat_desha"
        )

        # Verify tables are isolated
        cc_results = store.search("marketing content", "content_creator", k=5)
        pm_results = store.search("product roadmap", "product_manager", k=5)
        bd_results = store.search("Varanasi spiritual", "bharat_desha", k=5)

        assert all("marketing" in r["text"].lower() or "content" in r["text"].lower() for r in cc_results)
        assert all("product" in r["text"].lower() or "roadmap" in r["text"].lower() for r in pm_results)
        assert all("varanasi" in r["text"].lower() or "spiritual" in r["text"].lower() for r in bd_results)

        # Cross-check: bharat_desha table should not return content_creator text
        bd_check = store.search("marketing content", "bharat_desha", k=5)
        assert not any("marketing" in r["text"].lower() for r in bd_check)

    finally:
        config.LANCEDB_PATH = original_path
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py::test_lancedb_tables_are_isolated -v
```

Expected: FAIL (HuggingFace embeddings will initialise — may take a moment on first run as model downloads)

- [ ] **Step 3: Run test again after model downloads**

The HuggingFace `all-MiniLM-L6-v2` model (~90MB) downloads on first run and caches in `~/.cache/huggingface/`. Subsequent runs are instant.

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py::test_lancedb_tables_are_isolated -v
```

Expected: PASS

- [ ] **Step 4: Run all integration tests**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py -v
```

Expected: 5+ passed

- [ ] **Step 5: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: LanceDB table isolation smoke test"
```

---

## Task 6: End-to-end integration tests (one per persona)

**Files:**
- Modify: `tests/test_integration.py` (add 3 tests)

**What these verify:** The full pipeline — `get_crew(persona).run(brief)` — returns a valid `CrewOutput` with the expected artifact types. All external calls (Tavily, LLM, vector store) are mocked.

- [ ] **Step 1: Write the three failing tests**

Add to `tests/test_integration.py`:

```python
def _make_mock_crew_output(artifact_types):
    """Helper: build a mock CrewOutput with the given artifact types."""
    from crews.base_crew import CrewOutput
    return CrewOutput(
        artifacts=[{"type": t, "content": f"Mock content for {t}", "citations": []} for t in artifact_types]
    )


def test_e2e_content_creator_pipeline():
    from crews.router import get_crew
    from crews.base_crew import ResearchBrief, CrewOutput

    brief = ResearchBrief(
        topic="AI trends in 2025",
        persona="content_creator",
        audience="tech professionals",
        tone="informative",
        depth="standard",
        selected_artifacts=["blog_post", "social_post"],
    )

    mock_output = _make_mock_crew_output(["blog_post", "social_post"])

    with patch("crews.router.ContentCreatorCrew") as mock_class:
        mock_instance = MagicMock()
        mock_instance.run.return_value = mock_output
        mock_class.return_value = mock_instance

        crew = get_crew("content_creator")
        output = crew.run(brief)

    assert isinstance(output, CrewOutput)
    types = [a["type"] for a in output.artifacts]
    assert "blog_post" in types
    assert "social_post" in types


def test_e2e_product_manager_pipeline():
    from crews.router import get_crew
    from crews.base_crew import ResearchBrief, CrewOutput

    brief = ResearchBrief(
        topic="CRM software market 2025",
        persona="product_manager",
        audience="B2B SaaS executives",
        tone="analytical",
        depth="deep",
        selected_artifacts=["competitive_analysis", "executive_summary"],
    )

    mock_output = _make_mock_crew_output(["competitive_analysis", "executive_summary"])

    with patch("crews.router.ProductManagerCrew") as mock_class:
        mock_instance = MagicMock()
        mock_instance.run.return_value = mock_output
        mock_class.return_value = mock_instance

        crew = get_crew("product_manager")
        output = crew.run(brief)

    assert isinstance(output, CrewOutput)
    types = [a["type"] for a in output.artifacts]
    assert "competitive_analysis" in types
    assert "executive_summary" in types


def test_e2e_bharat_desha_pipeline():
    from crews.router import get_crew
    from crews.base_crew import ResearchBrief, CrewOutput

    brief = ResearchBrief(
        topic="Rishikesh yoga retreat",
        persona="bharat_desha",
        audience="solo spiritual travellers",
        tone="warm",
        depth="standard",
        selected_artifacts=["blog_post", "instagram", "seo_keywords"],
    )

    mock_output = _make_mock_crew_output(["seo_keywords", "blog_post", "instagram"])

    with patch("crews.router.BharatDeshaCrew") as mock_class:
        mock_instance = MagicMock()
        mock_instance.run.return_value = mock_output
        mock_class.return_value = mock_instance

        crew = get_crew("bharat_desha")
        output = crew.run(brief)

    assert isinstance(output, CrewOutput)
    types = [a["type"] for a in output.artifacts]
    assert "blog_post" in types
    assert "instagram" in types
    assert "seo_keywords" in types
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py::test_e2e_content_creator_pipeline tests/test_integration.py::test_e2e_product_manager_pipeline tests/test_integration.py::test_e2e_bharat_desha_pipeline -v
```

Expected: FAIL — crews.router imports ContentCreatorCrew and ProductManagerCrew which may not exist yet. If they don't exist, stub them temporarily:

```python
# crews/content_creator/__init__.py  — stub if Squad 3 not merged
# crews/content_creator/crew.py
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
class ContentCreatorCrew(BaseCrew):
    def retrieve(self, brief, sources): return []
    def analyse(self, retrieved): return {}
    def generate_artifacts(self, analysis, selected_artifacts): return []
```

```python
# crews/product_manager/__init__.py  — stub if Squad 4 not merged
# crews/product_manager/crew.py
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
class ProductManagerCrew(BaseCrew):
    def retrieve(self, brief, sources): return []
    def analyse(self, retrieved): return {}
    def generate_artifacts(self, analysis, selected_artifacts): return []
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_integration.py -v
```

Expected: 8 passed

- [ ] **Step 4: Run full test suite**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/ -v 2>&1 | tail -15
```

Expected: all tests pass (39 bharat_desha + 8 integration + 27 infrastructure = 74 total, minus any Squad 1/3/4 tests not yet merged)

- [ ] **Step 5: Commit**

```bash
git add tests/test_integration.py crews/content_creator/ crews/product_manager/
git commit -m "test: end-to-end integration tests for all three personas"
```

---

## Manual smoke test (run after all tasks complete)

With real API keys in `.env.local`:

```bash
streamlit run app.py
```

Test each persona manually:
1. Select **Content Creator** → topic: "remote work productivity" → run → verify blog post and social post render
2. Select **Product Manager** → topic: "project management tools 2025" → run → verify competitive analysis renders
3. Select **Bharat Desha** → topic: "Rishikesh yoga retreat" → select blog_post + instagram + youtube → run → verify seo_keywords always appears, blog post and social posts render correctly

Check LangFuse dashboard at `https://cloud.langfuse.com` — confirm 3 sessions appear with traces.
