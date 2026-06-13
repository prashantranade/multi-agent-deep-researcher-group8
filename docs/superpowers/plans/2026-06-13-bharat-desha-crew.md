# Bharat Desha Crew — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `BharatDeshaCrew` persona — a 6-agent pipeline that produces SEO-optimised India travel content (blog posts, itineraries, destination guides, wellness guides) and repurposes it into platform-specific social media copy (Instagram, Facebook, X, YouTube).

**Architecture:** Two upstream agents (Trend/Seasonality + SEO Keywords) feed into the standard retrieve → analyse → generate pipeline inherited from `BaseCrew`. Social repurposing runs as a final step for user-selected platforms. All agents share the existing `infrastructure/` layer (Tavily, LanceDB `bharat_desha` table, HuggingFace embeddings, OpenRouter LLM client).

**Tech Stack:** Python 3.11+, LangChain, Tavily API, LanceDB, HuggingFace `all-MiniLM-L6-v2` embeddings, `infrastructure/llm_client.py` (OpenRouter → Z.ai fallback), `config.INTAKE_MODEL` / `config.ANALYSIS_MODEL` / `config.OUTPUT_MODEL`

---

## Execution order

Tasks 1–7 are sequential (each builds on the previous). Task 8 wires everything together.

```
Task 1: crews/bharat_desha/__init__.py + config addition
Task 2: trend_agent.py
Task 3: seo_agent.py
Task 4: retrieval_agent.py
Task 5: analysis_agent.py
Task 6: content_agent.py
Task 7: social_agent.py
Task 8: crew.py (BharatDeshaCrew — orchestration)
```

---

## File structure

```
crews/
└── bharat_desha/
    ├── __init__.py          # Task 1 — exports BharatDeshaCrew
    ├── trend_agent.py       # Task 2 — Trend & Seasonality Agent
    ├── seo_agent.py         # Task 3 — SEO Keyword Agent
    ├── retrieval_agent.py   # Task 4 — Retrieval Agent
    ├── analysis_agent.py    # Task 5 — Analysis Agent
    ├── content_agent.py     # Task 6 — Content Generation Agent
    ├── social_agent.py      # Task 7 — Social Repurposing Agent
    └── crew.py              # Task 8 — BharatDeshaCrew(BaseCrew)

tests/
└── test_bharat_desha_crew.py   # tests added per task
```

**Existing files referenced (do not modify):**
- `crews/base_crew.py` — `BaseCrew`, `ResearchBrief`, `CrewOutput`
- `infrastructure/llm_client.py` — `chat_with_fallback(messages, model)`
- `infrastructure/vector_store.py` — `VectorStore`
- `config.py` — `INTAKE_MODEL`, `ANALYSIS_MODEL`, `OUTPUT_MODEL`, `TAVILY_API_KEY`, `LANCEDB_PATH`

---

## Task 1: Package init + config addition

**Files:**
- Create: `crews/bharat_desha/__init__.py`
- Modify: `config.py`
- Test: `tests/test_bharat_desha_crew.py` (create file)

- [ ] **Step 1: Write the failing test**

```python
# tests/test_bharat_desha_crew.py
import os
os.environ.setdefault("OPENROUTER_API_KEY", "x")
os.environ.setdefault("TAVILY_API_KEY", "x")

import config

def test_bharat_desha_table_config():
    assert config.BHARAT_DESHA_TABLE == "bharat_desha"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_bharat_desha_table_config -v
```

Expected: FAIL — `AttributeError: module 'config' has no attribute 'BHARAT_DESHA_TABLE'`

- [ ] **Step 3: Add config entry**

In `config.py`, append after the `LANCEDB_PATH` line:

```python
BHARAT_DESHA_TABLE = os.getenv("BHARAT_DESHA_TABLE", "bharat_desha")
```

- [ ] **Step 4: Create package init**

```python
# crews/bharat_desha/__init__.py
from .crew import BharatDeshaCrew

__all__ = ["BharatDeshaCrew"]
```

Note: `crew.py` doesn't exist yet — the import will fail until Task 8. That's fine; the test only checks config.

- [ ] **Step 5: Run test to verify it passes**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_bharat_desha_table_config -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add config.py crews/bharat_desha/__init__.py tests/test_bharat_desha_crew.py
git commit -m "feat: add bharat_desha package + config table name"
```

---

## Task 2: Trend & Seasonality Agent

**Files:**
- Create: `crews/bharat_desha/trend_agent.py`
- Modify: `tests/test_bharat_desha_crew.py`

**What this agent does:** Takes a raw topic string, runs two Tavily searches (trends + best time to visit), and returns a structured dict with `trends`, `seasonality`, and `topic_suggestions`.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_bharat_desha_crew.py`:

```python
from unittest.mock import patch, MagicMock

def test_trend_agent_returns_structured_output():
    from crews.bharat_desha.trend_agent import run_trend_agent

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"title": "Top spiritual destinations India 2025", "content": "Varanasi is trending..."},
            {"title": "Best time to visit Rishikesh", "content": "October to March is ideal..."},
        ]
    }

    mock_llm_response = """{
        "trends": ["Varanasi pilgrimages trending in 2025", "Yoga retreats in Rishikesh up 30%"],
        "seasonality": {
            "best_months": ["October", "November", "February", "March"],
            "avoid_months": ["June", "July", "August"],
            "active_festivals": ["Diwali (Oct)", "Mahashivratri (Feb)"],
            "advisories": []
        },
        "topic_suggestions": [
            "Varanasi spiritual guide for first-time visitors",
            "Rishikesh yoga retreat 7-day itinerary",
            "Best temples in Varanasi during Diwali"
        ]
    }"""

    with patch("crews.bharat_desha.trend_agent.TavilyClient", return_value=mock_tavily), \
         patch("crews.bharat_desha.trend_agent.chat_with_fallback", return_value=mock_llm_response):
        result = run_trend_agent("spiritual destinations Varanasi")

    assert "trends" in result
    assert "seasonality" in result
    assert "topic_suggestions" in result
    assert len(result["topic_suggestions"]) >= 1
    assert "best_months" in result["seasonality"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_trend_agent_returns_structured_output -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'crews.bharat_desha.trend_agent'`

- [ ] **Step 3: Implement trend_agent.py**

```python
# crews/bharat_desha/trend_agent.py
import json
from datetime import datetime
from tavily import TavilyClient
from infrastructure.llm_client import chat_with_fallback
import config

def run_trend_agent(topic: str) -> dict:
    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    year = datetime.now().year

    trends_results = client.search(f"{topic} India travel trends {year}", max_results=5)
    season_results = client.search(f"{topic} best time to visit India", max_results=5)

    combined = "\n\n".join(
        r["content"] for r in
        trends_results.get("results", []) + season_results.get("results", [])
        if r.get("content")
    )

    prompt = f"""You are a travel research analyst for BharatDesha, a spiritual India travel platform.

Analyse the following research about "{topic}" and return a JSON object with exactly these keys:
- "trends": list of 2-4 current trend observations (strings)
- "seasonality": object with keys "best_months" (list), "avoid_months" (list), "active_festivals" (list), "advisories" (list)
- "topic_suggestions": list of 3-5 refined topic variations the content creator can choose from

Research:
{combined}

Return only valid JSON. No markdown, no explanation."""

    response = chat_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        model=config.INTAKE_MODEL,
    )

    return json.loads(response)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_trend_agent_returns_structured_output -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crews/bharat_desha/trend_agent.py tests/test_bharat_desha_crew.py
git commit -m "feat: add bharat_desha trend & seasonality agent"
```

---

## Task 3: SEO Keyword Agent

**Files:**
- Create: `crews/bharat_desha/seo_agent.py`
- Modify: `tests/test_bharat_desha_crew.py`

**What this agent does:** Takes a confirmed topic + trend context, searches for top-ranking content, and extracts the 10 most relevant SEO keywords with search intent labels.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_bharat_desha_crew.py`:

```python
def test_seo_agent_returns_ten_keywords():
    from crews.bharat_desha.seo_agent import run_seo_agent

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"content": "Varanasi ghats spiritual guide Kashi Vishwanath temple Ganga aarti"},
        ]
    }

    mock_llm_response = """{
        "keywords": [
            {"keyword": "Varanasi spiritual tour", "intent": "informational"},
            {"keyword": "Kashi Vishwanath temple guide", "intent": "informational"},
            {"keyword": "Ganga aarti Varanasi", "intent": "informational"},
            {"keyword": "Varanasi ghats walk", "intent": "informational"},
            {"keyword": "best time to visit Varanasi", "intent": "informational"},
            {"keyword": "Varanasi pilgrimage package", "intent": "transactional"},
            {"keyword": "Manikarnika ghat Varanasi", "intent": "navigational"},
            {"keyword": "Varanasi boat ride at sunrise", "intent": "informational"},
            {"keyword": "Sanatan Dharma sacred city India", "intent": "informational"},
            {"keyword": "Varanasi travel tips first time", "intent": "informational"}
        ],
        "primary_keyword": "Varanasi spiritual tour"
    }"""

    trend_context = {"trends": ["Varanasi pilgrimages trending"], "seasonality": {}, "topic_suggestions": []}

    with patch("crews.bharat_desha.seo_agent.TavilyClient", return_value=mock_tavily), \
         patch("crews.bharat_desha.seo_agent.chat_with_fallback", return_value=mock_llm_response):
        result = run_seo_agent("Varanasi spiritual tour", trend_context)

    assert "keywords" in result
    assert len(result["keywords"]) == 10
    assert "primary_keyword" in result
    assert all("keyword" in k and "intent" in k for k in result["keywords"])
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_seo_agent_returns_ten_keywords -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'crews.bharat_desha.seo_agent'`

- [ ] **Step 3: Implement seo_agent.py**

```python
# crews/bharat_desha/seo_agent.py
import json
from tavily import TavilyClient
from infrastructure.llm_client import chat_with_fallback
import config

def run_seo_agent(topic: str, trend_context: dict) -> dict:
    client = TavilyClient(api_key=config.TAVILY_API_KEY)

    results = client.search(f"{topic} India travel guide", max_results=8)
    combined = "\n\n".join(
        r["content"] for r in results.get("results", []) if r.get("content")
    )

    trends_summary = ", ".join(trend_context.get("trends", []))

    prompt = f"""You are an SEO specialist for BharatDesha, a spiritual India travel platform.

Topic: "{topic}"
Current trends: {trends_summary}

Analyse the following top-ranking content and extract exactly 10 SEO keywords.

Return a JSON object with:
- "keywords": list of exactly 10 objects, each with "keyword" (string) and "intent" ("informational"|"navigational"|"transactional")
- "primary_keyword": the single most important keyword (string)

Focus on India travel, Sanatan Dharma, spiritual tourism, and wellness keywords.

Top-ranking content:
{combined}

Return only valid JSON. No markdown, no explanation."""

    response = chat_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        model=config.INTAKE_MODEL,
    )

    return json.loads(response)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_seo_agent_returns_ten_keywords -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crews/bharat_desha/seo_agent.py tests/test_bharat_desha_crew.py
git commit -m "feat: add bharat_desha SEO keyword agent"
```

---

## Task 4: Retrieval Agent

**Files:**
- Create: `crews/bharat_desha/retrieval_agent.py`
- Modify: `tests/test_bharat_desha_crew.py`

**What this agent does:** Searches for sources via Tavily using topic + top keywords, scrapes content with BeautifulSoup, stores chunks in LanceDB table `bharat_desha`, returns retrieved chunks.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_bharat_desha_crew.py`:

```python
def test_retrieval_agent_returns_chunks():
    from crews.bharat_desha.retrieval_agent import run_retrieval_agent

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"url": "https://example.com/varanasi", "title": "Varanasi Guide", "content": "Varanasi is the spiritual capital of India..."},
        ]
    }

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = [
        {"text": "Varanasi is the spiritual capital of India...", "metadata": {"source": "https://example.com/varanasi"}}
    ]

    seo_context = {
        "keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}],
        "primary_keyword": "Varanasi spiritual tour"
    }

    with patch("crews.bharat_desha.retrieval_agent.TavilyClient", return_value=mock_tavily), \
         patch("crews.bharat_desha.retrieval_agent.VectorStore", return_value=mock_vector_store):
        result = run_retrieval_agent("Varanasi spiritual tour", seo_context)

    assert isinstance(result, list)
    assert len(result) > 0
    assert "text" in result[0]
    assert "metadata" in result[0]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_retrieval_agent_returns_chunks -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'crews.bharat_desha.retrieval_agent'`

- [ ] **Step 3: Implement retrieval_agent.py**

```python
# crews/bharat_desha/retrieval_agent.py
from tavily import TavilyClient
from infrastructure.vector_store import VectorStore
import config

_CHUNK_SIZE = 400  # characters per chunk

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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_retrieval_agent_returns_chunks -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crews/bharat_desha/retrieval_agent.py tests/test_bharat_desha_crew.py
git commit -m "feat: add bharat_desha retrieval agent"
```

---

## Task 5: Analysis Agent

**Files:**
- Create: `crews/bharat_desha/analysis_agent.py`
- Modify: `tests/test_bharat_desha_crew.py`

**What this agent does:** Synthesises retrieved chunks through the BharatDesha lens — spiritual significance, practical logistics, cultural authenticity, wellness angle, and seasonal framing.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_bharat_desha_crew.py`:

```python
def test_analysis_agent_returns_bharat_desha_lens():
    from crews.bharat_desha.analysis_agent import run_analysis_agent

    retrieved = [
        {"text": "Varanasi is considered the holiest city in Hinduism...", "metadata": {"source": "https://example.com"}},
        {"text": "Best time to visit is October to March for ghats walk...", "metadata": {"source": "https://example.com"}},
    ]
    seo_context = {"keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}], "primary_keyword": "Varanasi spiritual tour"}
    trend_context = {"seasonality": {"best_months": ["October", "March"], "active_festivals": ["Diwali"]}, "trends": []}

    mock_response = """{
        "spiritual": "Varanasi is the abode of Lord Shiva, one of the 12 Jyotirlingas...",
        "practical": "Fly to Varanasi airport (VNS), auto-rickshaw to ghats costs 150 INR...",
        "cultural": "Ganga aarti at Dashashwamedh Ghat runs every evening at 7pm...",
        "wellness": "Several ashrams offer 5-day yoga and meditation retreats near Assi Ghat...",
        "seasonal": "October to March is ideal; avoid June-August monsoon...",
        "key_points": ["Visit Kashi Vishwanath temple at dawn", "Sunrise boat ride on the Ganga"],
        "citations": ["https://example.com"]
    }"""

    with patch("crews.bharat_desha.analysis_agent.chat_with_fallback", return_value=mock_response):
        result = run_analysis_agent(retrieved, seo_context, trend_context)

    for key in ["spiritual", "practical", "cultural", "wellness", "seasonal", "key_points", "citations"]:
        assert key in result
    assert isinstance(result["key_points"], list)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_analysis_agent_returns_bharat_desha_lens -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement analysis_agent.py**

```python
# crews/bharat_desha/analysis_agent.py
import json
from typing import List, Dict
from infrastructure.llm_client import chat_with_fallback
import config

def run_analysis_agent(retrieved: List[Dict], seo_context: dict, trend_context: dict) -> dict:
    context = "\n\n".join(r["text"] for r in retrieved)
    keywords = ", ".join(k["keyword"] for k in seo_context.get("keywords", []))
    seasonality = trend_context.get("seasonality", {})
    festivals = ", ".join(seasonality.get("active_festivals", [])) or "none noted"
    best_months = ", ".join(seasonality.get("best_months", [])) or "year-round"

    prompt = f"""You are a senior researcher for BharatDesha, a spiritual India travel platform.

Analyse the research below through the BharatDesha lens and return a JSON object with exactly these keys:
- "spiritual": paragraph on spiritual significance (Vedic context, sacred geography, Sanatan Dharma)
- "practical": paragraph on logistics (transport, accommodation, costs, safety tips)
- "cultural": paragraph on cultural authenticity (customs, festivals, food, community)
- "wellness": paragraph on wellness angle (yoga, meditation, sound healing, Ayurveda if relevant)
- "seasonal": paragraph on best timing, festivals, and seasonal considerations
- "key_points": list of 5-8 bullet points summarising the most important takeaways
- "citations": list of source URLs from the research

SEO keywords to weave in: {keywords}
Active festivals: {festivals}
Best travel months: {best_months}

Research:
{context}

Return only valid JSON. No markdown, no explanation."""

    response = chat_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        model=config.ANALYSIS_MODEL,
    )

    return json.loads(response)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_analysis_agent_returns_bharat_desha_lens -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add crews/bharat_desha/analysis_agent.py tests/test_bharat_desha_crew.py
git commit -m "feat: add bharat_desha analysis agent"
```

---

## Task 6: Content Agent

**Files:**
- Create: `crews/bharat_desha/content_agent.py`
- Modify: `tests/test_bharat_desha_crew.py`

**What this agent does:** Generates the primary content artifact (blog_post, itinerary, destination_guide, or wellness_guide) from the analysis, weaving in all 10 SEO keywords.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_bharat_desha_crew.py`:

```python
def test_content_agent_generates_blog_post():
    from crews.bharat_desha.content_agent import run_content_agent

    analysis = {
        "spiritual": "Varanasi is the abode of Lord Shiva...",
        "practical": "Fly into VNS airport...",
        "cultural": "Ganga aarti at Dashashwamedh Ghat...",
        "wellness": "Several ashrams near Assi Ghat...",
        "seasonal": "October to March is ideal...",
        "key_points": ["Visit at dawn", "Sunrise boat ride"],
        "citations": ["https://example.com"]
    }
    seo_context = {
        "keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}],
        "primary_keyword": "Varanasi spiritual tour"
    }

    mock_response = "# Varanasi Spiritual Tour: Your Complete Guide\n\nVaranasi spiritual tour begins at dawn..."

    with patch("crews.bharat_desha.content_agent.chat_with_fallback", return_value=mock_response):
        result = run_content_agent(analysis, seo_context, artifact_type="blog_post", tone="warm", depth="standard")

    assert result["type"] == "blog_post"
    assert len(result["content"]) > 100
    assert "citations" in result

def test_content_agent_generates_itinerary():
    from crews.bharat_desha.content_agent import run_content_agent

    analysis = {
        "spiritual": "...", "practical": "...", "cultural": "...",
        "wellness": "...", "seasonal": "...",
        "key_points": ["Day 1: Arrive", "Day 2: Ghats"],
        "citations": ["https://example.com"]
    }
    seo_context = {"keywords": [], "primary_keyword": "Varanasi itinerary"}

    mock_response = "## Day 1: Arrival in Varanasi\n\nCheck into your hotel near Assi Ghat..."

    with patch("crews.bharat_desha.content_agent.chat_with_fallback", return_value=mock_response):
        result = run_content_agent(analysis, seo_context, artifact_type="itinerary", tone="practical", depth="deep")

    assert result["type"] == "itinerary"
    assert "content" in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_content_agent_generates_blog_post tests/test_bharat_desha_crew.py::test_content_agent_generates_itinerary -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement content_agent.py**

```python
# crews/bharat_desha/content_agent.py
from typing import Dict
from infrastructure.llm_client import chat_with_fallback
import config

_ARTIFACT_INSTRUCTIONS = {
    "blog_post": "Write an 800-1500 word SEO-optimised blog post with H2/H3 headings. Include the primary keyword in the title and opening paragraph.",
    "itinerary": "Write a day-by-day travel itinerary with timings, transport options, accommodation suggestions, and spiritual stops. Be specific and practical.",
    "destination_guide": "Write a comprehensive destination guide structured by theme: Getting There, Spiritual Highlights, Cultural Experiences, Practical Tips, Best Time to Visit.",
    "wellness_guide": "Write a wellness-focused guide covering yoga retreats, meditation centres, sound healing, Ayurveda treatments, and ashram stays. Include pricing where possible.",
}

def run_content_agent(analysis: Dict, seo_context: dict, artifact_type: str, tone: str, depth: str) -> Dict:
    keywords = ", ".join(k["keyword"] for k in seo_context.get("keywords", []))
    primary_keyword = seo_context.get("primary_keyword", "")
    instruction = _ARTIFACT_INSTRUCTIONS.get(artifact_type, _ARTIFACT_INSTRUCTIONS["blog_post"])

    prompt = f"""You are a content writer for BharatDesha, a spiritual India travel platform.
Tone: {tone}. Depth: {depth}.

{instruction}

Weave these SEO keywords naturally throughout the content: {keywords}
Primary keyword "{primary_keyword}" must appear in the first 100 words.

Research summary:
- Spiritual: {analysis["spiritual"]}
- Practical: {analysis["practical"]}
- Cultural: {analysis["cultural"]}
- Wellness: {analysis["wellness"]}
- Seasonal: {analysis["seasonal"]}
- Key points: {", ".join(analysis["key_points"])}

Write the content now. Use markdown formatting."""

    content = chat_with_fallback(
        messages=[{"role": "user", "content": prompt}],
        model=config.OUTPUT_MODEL,
    )

    return {
        "type": artifact_type,
        "content": content,
        "citations": analysis.get("citations", []),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_content_agent_generates_blog_post tests/test_bharat_desha_crew.py::test_content_agent_generates_itinerary -v
```

Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add crews/bharat_desha/content_agent.py tests/test_bharat_desha_crew.py
git commit -m "feat: add bharat_desha content agent"
```

---

## Task 7: Social Repurposing Agent

**Files:**
- Create: `crews/bharat_desha/social_agent.py`
- Modify: `tests/test_bharat_desha_crew.py`

**What this agent does:** Takes the primary content artifact + analysis key_points and generates platform-specific social copy for each platform the user selected.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_bharat_desha_crew.py`:

```python
def test_social_agent_generates_instagram():
    from crews.bharat_desha.social_agent import run_social_agent

    primary_artifact = {
        "type": "blog_post",
        "content": "# Varanasi Spiritual Tour\n\nVaranasi spiritual tour begins at dawn...",
        "citations": []
    }
    key_points = ["Visit Kashi Vishwanath at dawn", "Sunrise boat ride on the Ganga"]
    seo_context = {"primary_keyword": "Varanasi spiritual tour", "keywords": []}

    mock_response = "Step into the sacred energy of Varanasi 🕉️ The ghats come alive at dawn...\n\n#VaranasiTravel #SpiritualIndia #BharatDesha"

    with patch("crews.bharat_desha.social_agent.chat_with_fallback", return_value=mock_response):
        results = run_social_agent(primary_artifact, key_points, seo_context, platforms=["instagram"])

    assert len(results) == 1
    assert results[0]["type"] == "instagram"
    assert len(results[0]["content"]) > 50

def test_social_agent_generates_multiple_platforms():
    from crews.bharat_desha.social_agent import run_social_agent

    primary_artifact = {"type": "blog_post", "content": "Varanasi guide...", "citations": []}
    key_points = ["Key point 1"]
    seo_context = {"primary_keyword": "Varanasi guide", "keywords": []}

    with patch("crews.bharat_desha.social_agent.chat_with_fallback", return_value="mock social content"):
        results = run_social_agent(primary_artifact, key_points, seo_context, platforms=["instagram", "facebook", "x_post", "youtube"])

    assert len(results) == 4
    types = [r["type"] for r in results]
    assert set(types) == {"instagram", "facebook", "x_post", "youtube"}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_social_agent_generates_instagram tests/test_bharat_desha_crew.py::test_social_agent_generates_multiple_platforms -v
```

Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement social_agent.py**

```python
# crews/bharat_desha/social_agent.py
from typing import List, Dict
from infrastructure.llm_client import chat_with_fallback
import config

_PLATFORM_PROMPTS = {
    "instagram": """Write an Instagram caption for BharatDesha (spiritual India travel).
- 150-220 words, warm and evocative tone
- End with exactly 15 hashtags on a new line (mix broad India travel + niche spiritual tags)
- Include the primary keyword naturally
- No emojis required but welcome if natural""",

    "facebook": """Write a Facebook post for BharatDesha (spiritual India travel).
- 100-150 words, informative and engaging
- Follow with 2 sentences of link preview text (label it "Link preview:")
- Include the primary keyword naturally""",

    "x_post": """Write an X (Twitter) thread for BharatDesha (spiritual India travel).
- 5 tweets, each under 280 characters
- Number each tweet (1/5, 2/5, etc.)
- First tweet must hook attention and include the primary keyword
- Last tweet ends with a call to action""",

    "youtube": """Write YouTube metadata for BharatDesha (spiritual India travel).
- Title: under 70 characters, primary keyword first
- Description: 300 words, first 2 sentences hook viewers, includes keywords naturally
- 5 chapter suggestions with placeholder timestamps (e.g. 0:00 Introduction)
Format as:
TITLE: ...
DESCRIPTION: ...
CHAPTERS:
0:00 ...""",
}

def run_social_agent(primary_artifact: Dict, key_points: List[str], seo_context: dict, platforms: List[str]) -> List[Dict]:
    primary_keyword = seo_context.get("primary_keyword", "")
    points_summary = "\n".join(f"- {p}" for p in key_points)
    content_snippet = primary_artifact["content"][:600]

    artifacts = []
    for platform in platforms:
        platform_instruction = _PLATFORM_PROMPTS.get(platform, _PLATFORM_PROMPTS["instagram"])

        prompt = f"""{platform_instruction}

Primary keyword: {primary_keyword}
Key points from the article:
{points_summary}

Article excerpt:
{content_snippet}

Write the content now."""

        content = chat_with_fallback(
            messages=[{"role": "user", "content": prompt}],
            model=config.OUTPUT_MODEL,
        )
        artifacts.append({"type": platform, "content": content})

    return artifacts
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_social_agent_generates_instagram tests/test_bharat_desha_crew.py::test_social_agent_generates_multiple_platforms -v
```

Expected: 2 PASS

- [ ] **Step 5: Commit**

```bash
git add crews/bharat_desha/social_agent.py tests/test_bharat_desha_crew.py
git commit -m "feat: add bharat_desha social repurposing agent"
```

---

## Task 8: BharatDeshaCrew — Orchestration

**Files:**
- Create: `crews/bharat_desha/crew.py`
- Modify: `tests/test_bharat_desha_crew.py`

**What this does:** Wires all 6 agents into a single `BharatDeshaCrew(BaseCrew)` class. Implements the three abstract methods (`retrieve`, `analyse`, `generate_artifacts`) and extends `run()` to prepend the trend + SEO pipeline.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_bharat_desha_crew.py`:

```python
def test_bharat_desha_crew_run_returns_crew_output():
    from crews.bharat_desha.crew import BharatDeshaCrew
    from crews.base_crew import ResearchBrief, CrewOutput

    brief = ResearchBrief(
        topic="Varanasi spiritual tour",
        persona="bharat_desha",
        audience="solo spiritual travellers",
        tone="warm",
        depth="standard",
        selected_artifacts=["blog_post", "instagram"],
    )

    mock_trend = {
        "trends": ["Varanasi trending"],
        "seasonality": {"best_months": ["October"], "avoid_months": [], "active_festivals": [], "advisories": []},
        "topic_suggestions": ["Varanasi ghats guide"]
    }
    mock_seo = {
        "keywords": [{"keyword": "Varanasi spiritual tour", "intent": "informational"}],
        "primary_keyword": "Varanasi spiritual tour"
    }
    mock_retrieved = [{"text": "Varanasi is sacred...", "metadata": {"source": "https://example.com"}}]
    mock_analysis = {
        "spiritual": "Sacred city...", "practical": "Fly to VNS...",
        "cultural": "Ganga aarti...", "wellness": "Ashrams nearby...",
        "seasonal": "Oct-March best...",
        "key_points": ["Visit at dawn"],
        "citations": ["https://example.com"]
    }
    mock_blog = {"type": "blog_post", "content": "# Varanasi Guide\n\n...", "citations": []}
    mock_social = [{"type": "instagram", "content": "Caption here..."}]
    mock_seo_artifact = {"type": "seo_keywords", "content": "1. Varanasi spiritual tour\n..."}

    with patch("crews.bharat_desha.crew.run_trend_agent", return_value=mock_trend), \
         patch("crews.bharat_desha.crew.run_seo_agent", return_value=mock_seo), \
         patch("crews.bharat_desha.crew.run_retrieval_agent", return_value=mock_retrieved), \
         patch("crews.bharat_desha.crew.run_analysis_agent", return_value=mock_analysis), \
         patch("crews.bharat_desha.crew.run_content_agent", return_value=mock_blog), \
         patch("crews.bharat_desha.crew.run_social_agent", return_value=mock_social):

        crew = BharatDeshaCrew()
        output = crew.run(brief)

    assert isinstance(output, CrewOutput)
    artifact_types = [a["type"] for a in output.artifacts]
    assert "blog_post" in artifact_types
    assert "instagram" in artifact_types
    assert "seo_keywords" in artifact_types   # always included
```

- [ ] **Step 2: Run test to verify it fails**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_bharat_desha_crew_run_returns_crew_output -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'crews.bharat_desha.crew'`

- [ ] **Step 3: Implement crew.py**

```python
# crews/bharat_desha/crew.py
from typing import List, Dict, Any
from crews.base_crew import BaseCrew, ResearchBrief, CrewOutput
from crews.bharat_desha.trend_agent import run_trend_agent
from crews.bharat_desha.seo_agent import run_seo_agent
from crews.bharat_desha.retrieval_agent import run_retrieval_agent
from crews.bharat_desha.analysis_agent import run_analysis_agent
from crews.bharat_desha.content_agent import run_content_agent
from crews.bharat_desha.social_agent import run_social_agent

_SOCIAL_PLATFORMS = {"instagram", "facebook", "x_post", "youtube"}
_PRIMARY_CONTENT_TYPES = {"blog_post", "itinerary", "destination_guide", "wellness_guide"}

class BharatDeshaCrew(BaseCrew):

    def retrieve(self, brief: ResearchBrief, sources: List[Dict]) -> List[Dict[str, Any]]:
        return run_retrieval_agent(brief.topic, self._seo_context)

    def analyse(self, retrieved: List[Dict[str, Any]]) -> Dict[str, Any]:
        return run_analysis_agent(retrieved, self._seo_context, self._trend_context)

    def generate_artifacts(self, analysis: Dict[str, Any], selected_artifacts: List[str]) -> List[Dict[str, Any]]:
        artifacts = []

        # SEO keywords artifact — always included
        keyword_lines = "\n".join(
            f"{i+1}. {k['keyword']} ({k['intent']})"
            for i, k in enumerate(self._seo_context.get("keywords", []))
        )
        artifacts.append({"type": "seo_keywords", "content": keyword_lines, "citations": []})

        # Primary content artifact
        primary_type = next((a for a in selected_artifacts if a in _PRIMARY_CONTENT_TYPES), None)
        primary_artifact = None
        if primary_type:
            primary_artifact = run_content_agent(
                analysis, self._seo_context,
                artifact_type=primary_type,
                tone=self._brief.tone,
                depth=self._brief.depth,
            )
            artifacts.append(primary_artifact)

        # Social repurposing — only for selected platforms
        selected_platforms = [a for a in selected_artifacts if a in _SOCIAL_PLATFORMS]
        if selected_platforms and primary_artifact:
            social_artifacts = run_social_agent(
                primary_artifact,
                analysis.get("key_points", []),
                self._seo_context,
                platforms=selected_platforms,
            )
            artifacts.extend(social_artifacts)

        return artifacts

    def run(self, brief: ResearchBrief) -> CrewOutput:
        self._brief = brief
        self._trend_context = run_trend_agent(brief.topic)
        self._seo_context = run_seo_agent(brief.topic, self._trend_context)

        retrieved = self.retrieve(brief, brief.selected_sources)
        analysis = self.analyse(retrieved)
        artifacts = self.generate_artifacts(analysis, brief.selected_artifacts)
        return CrewOutput(artifacts=artifacts)
```

- [ ] **Step 4: Run test to verify it passes**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/test_bharat_desha_crew.py::test_bharat_desha_crew_run_returns_crew_output -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite**

```bash
OPENROUTER_API_KEY=x TAVILY_API_KEY=x pytest tests/ -v
```

Expected: all tests pass (27 existing + 10 new = 37 total)

- [ ] **Step 6: Commit**

```bash
git add crews/bharat_desha/crew.py tests/test_bharat_desha_crew.py
git commit -m "feat: add BharatDeshaCrew orchestration — full 6-agent pipeline"
```

---

## Verification

After Task 8, verify the full pipeline end-to-end with real API keys:

```python
# run this in a Python REPL with your .env.local loaded
import config
from crews.base_crew import ResearchBrief
from crews.bharat_desha.crew import BharatDeshaCrew

brief = ResearchBrief(
    topic="Rishikesh yoga retreat",
    persona="bharat_desha",
    audience="solo spiritual travellers from the West",
    tone="warm and knowledgeable",
    depth="standard",
    selected_artifacts=["blog_post", "instagram", "youtube"],
)

crew = BharatDeshaCrew()
output = crew.run(brief)

for a in output.artifacts:
    print(f"\n=== {a['type'].upper()} ===\n{a['content'][:300]}\n")
```

Expected: trend context logged, SEO keywords generated, blog post + Instagram caption + YouTube metadata printed.
