# Bharat Desha Persona — Design Spec

**Date:** 2026-06-13
**Status:** Approved

---

## Overview

Bharat Desha ([bharatdesha.com](https://www.bharatdesha.com)) is a spiritual and practical India travel platform targeting solo explorers and spiritual seekers. It bridges Vedic wisdom with modern travel logistics, covering destinations, Sanatan Dharma philosophy, festivals, yoga/wellness retreats, and on-the-ground guidance.

This spec defines the `bharat_desha` crew — a new persona added to the Multi-Agent Deep Researcher that enables BharatDesha content creators to research and produce SEO-optimised travel content, repurposed across social platforms.

---

## Goal

Build a `BharatDeshaCrew` that plugs into the existing `BaseCrew` contract, producing:
1. SEO-optimised primary content (blog posts, itineraries, destination guides, wellness guides)
2. Platform-specific social media copy (Instagram, Facebook, X, YouTube)
3. Upstream intelligence (trend/seasonality research + SEO keywords) that shapes all content

---

## Architecture

The pipeline adds two upstream agents (Trend/Seasonality and SEO Keywords) before the standard retrieve → analyse → generate flow. Social repurposing runs after primary content generation.

```
[Trend & Seasonality Agent]
         ↓  trends, seasonality, 3–5 topic suggestions
[SEO Keyword Agent]
         ↓  top 10 keywords (mandatory, used by all downstream agents)
[Retrieval Agent]    ← Tavily search + BeautifulSoup scrape → LanceDB (bharat_desha table)
         ↓
[Analysis Agent]     ← BharatDesha lens: spiritual + practical + cultural authenticity
         ↓
[Content Agent]      ← primary artifact (blog / itinerary / destination guide / wellness guide)
         ↓
[Social Repurposing Agent]  ← runs only for user-selected platforms
         ↓
[CrewOutput]         ← primary artifact + social artifacts + seo_keywords (always)
```

**Integration points:**
- `ResearchBrief.persona = "bharat_desha"` — no change to `BaseCrew` or `ResearchBrief` needed
- `ResearchBrief.selected_artifacts` carries user's platform selections
- LanceDB table: `bharat_desha` (isolated from `content_creator` and `product_manager`)
- All LLM calls via `infrastructure/llm_client.py` (OpenRouter → Z.ai fallback)
- Observability via `observability/langfuse_client.py`

---

## Agent Details

### 1. Trend & Seasonality Agent (`trend_agent.py`)

**Purpose:** Research current travel conditions and suggest topic variations before content is committed.

**Inputs:** raw topic string from `ResearchBrief.topic`

**Process:**
- Tavily search: `"{topic} India travel trends {current_year}"` and `"{topic} best time to visit India"`
- Extracts: trending destinations/experiences, seasonal windows, active festivals, travel advisories
- Generates 3–5 topic variations the researcher can choose from before proceeding

**Output:**
```python
{
    "trends": [...],           # list of current trend observations
    "seasonality": {
        "best_months": [...],
        "avoid_months": [...],
        "active_festivals": [...],
        "advisories": [...]
    },
    "topic_suggestions": [...]  # 3–5 refined topic options
}
```

**Note:** The researcher sees this output and confirms or adjusts the topic before the SEO agent runs.

---

### 2. SEO Keyword Agent (`seo_agent.py`)

**Purpose:** Identify the top 10 search keywords for the confirmed topic. All downstream content must incorporate these keywords.

**Inputs:** confirmed topic, trend context from Trend Agent

**Process:**
- Tavily search: `"{topic} India travel keywords"`, `"{topic} Sanatan Dharma guide"`, etc.
- Analyses top-ranking pages for keyword patterns
- Filters for India/spiritual/wellness relevance
- Returns ordered list of 10 keywords with estimated search intent

**Output:**
```python
{
    "keywords": [
        {"keyword": str, "intent": "informational|navigational|transactional"},
        ...  # 10 total
    ],
    "primary_keyword": str   # top keyword, used as article focus
}
```

**Note:** `seo_keywords` artifact is always included in `CrewOutput` regardless of user's artifact selection.

---

### 3. Retrieval Agent (`retrieval_agent.py`)

**Purpose:** Source authoritative content on the confirmed topic using Tavily + deep scraping, stored in LanceDB for retrieval.

**Inputs:** confirmed topic, SEO keywords, `ResearchBrief.selected_sources`

**Process:**
- Tavily search using topic + top 3 keywords
- BeautifulSoup deep-scrape of top results
- Chunk text, embed via HuggingFace (`all-MiniLM-L6-v2`), store in LanceDB table `bharat_desha`
- Semantic search to retrieve most relevant chunks

**Output:** list of retrieved chunks with source metadata (url, title, date)

---

### 4. Analysis Agent (`analysis_agent.py`)

**Purpose:** Synthesise retrieved content through the BharatDesha lens.

**Inputs:** retrieved chunks, SEO keywords, trend/seasonality context

**BharatDesha lens — every analysis must include:**
- **Spiritual significance** — Vedic context, Sanatan Dharma relevance, sacred geography
- **Practical logistics** — transport, accommodation, timing, costs, safety
- **Cultural authenticity** — local customs, festivals, food, community practices
- **Wellness angle** — yoga, meditation, sound healing, Ayurveda if relevant
- **Seasonal framing** — best time to experience, what changes by season

**Output:**
```python
{
    "spiritual": str,
    "practical": str,
    "cultural": str,
    "wellness": str,
    "seasonal": str,
    "key_points": [...],   # bullet list used by Content + Social agents
    "citations": [...]
}
```

---

### 5. Content Agent (`content_agent.py`)

**Purpose:** Generate the primary content artifact, fully SEO-optimised.

**Inputs:** analysis dict, SEO keywords, selected primary artifact type, `ResearchBrief.tone` and `depth`

**Artifact types:**
- `blog_post` — 800–1500 words, H2/H3 structure, SEO keywords in headings and first 100 words
- `itinerary` — day-by-day plan with timings, transport, accommodation, spiritual stops
- `destination_guide` — cultural + spiritual + practical overview, structured by theme
- `wellness_guide` — yoga, meditation, sound healing, Ayurveda retreats focus

**Requirements:**
- Primary keyword in title and opening paragraph
- All 10 SEO keywords woven naturally into content
- Citations inline
- Seasonal timing note included

**Output:** single `CrewOutput` artifact `{"type": artifact_type, "content": str, "citations": [...]}`

---

### 6. Social Repurposing Agent (`social_agent.py`)

**Purpose:** Repurpose primary content into platform-specific social assets.

**Inputs:** primary artifact, analysis key_points, SEO keywords, user's selected platforms

**Runs only for selected platforms:**

| Platform | Output |
|---|---|
| `instagram` | Caption (150–220 words) + 15 hashtags (mix of broad/niche India travel tags) |
| `facebook` | Post (100–150 words) + link preview text (2 sentences) |
| `x_post` | Thread of 5 tweets (each ≤280 chars) OR single post if topic is simple |
| `youtube` | Title (≤70 chars, primary keyword first) + Description (300 words) + 5 chapter suggestions with timestamps |

**Each platform output:**
- References 3–5 key points from the primary content
- Includes primary keyword and 2–3 secondary keywords naturally
- Matches BharatDesha tone: warm, knowledgeable, spiritually grounded, practically useful

**Output:** one artifact per selected platform, same `{"type": platform, "content": str}` shape

---

## Artifacts Reference

| Artifact key | Always included | User-selectable |
|---|---|---|
| `seo_keywords` | ✅ | — |
| `trend_report` | ✅ (shown at intake) | — |
| `blog_post` | — | ✅ |
| `itinerary` | — | ✅ |
| `destination_guide` | — | ✅ |
| `wellness_guide` | — | ✅ |
| `instagram` | — | ✅ |
| `facebook` | — | ✅ |
| `x_post` | — | ✅ |
| `youtube` | — | ✅ |

---

## File Structure

```
crews/bharat_desha/
├── __init__.py
├── crew.py            # BharatDeshaCrew(BaseCrew) — orchestrates full pipeline
├── trend_agent.py     # Trend & Seasonality Agent
├── seo_agent.py       # SEO Keyword Agent
├── retrieval_agent.py # Retrieval Agent (Tavily + LanceDB bharat_desha table)
├── analysis_agent.py  # Analysis Agent (BharatDesha lens)
├── content_agent.py   # Primary content generation
└── social_agent.py    # Social repurposing (Instagram, Facebook, X, YouTube)

tests/
└── test_bharat_desha_crew.py   # unit tests for all 6 agents + crew orchestration
```

---

## Config Changes

No new API keys required. All LLM calls use existing OpenRouter setup.

`config.py` addition:
```python
BHARAT_DESHA_TABLE = os.getenv("BHARAT_DESHA_TABLE", "bharat_desha")
```

`AVAILABLE_MODELS` in `config.py` already covers the model needs. No changes to `BaseCrew`, `ResearchBrief`, or `CrewOutput`.

---

## Out of Scope (Post-Hackathon)

- Image sourcing via Unsplash API
- Canva design template generation for social posts
- Phot.ai ad creative integration
- Paid travel advisory data sources
