# Task 20: Integration Design Spec

**Date:** 2026-06-13
**Status:** Approved

---

## Goal

Wire all four squads' work into a single working application. After integration, a user can open the Streamlit app, select any persona (Content Creator, Product Manager, Bharat Desha), complete the 7-step guided intake flow, and receive persona-specific artifacts including social media content.

---

## What integration covers

Integration does NOT rewrite squad work. It wires existing pieces together:

1. **Persona routing** — `app.py` maps `ResearchBrief.persona` to the correct crew class
2. **Persona selector UI** — Bharat Desha added as a selectable persona with correct artifact options
3. **Artifact renderer** — UI renders all artifact types including BharatDesha-specific ones (`seo_keywords`, `x_post`, `youtube`, `wellness_guide`)
4. **LanceDB isolation check** — confirm each crew uses its own table, no cross-contamination
5. **LangFuse session wiring** — session_id flows from app.py through to each crew run
6. **End-to-end smoke test** — one automated integration test per persona that mocks all external calls and verifies the full pipeline returns valid `CrewOutput`

---

## Assumptions about squad outputs

Integration assumes each squad has delivered:

**Squad 1 (intake + UI):**
- `app.py` — Streamlit entry point with 7-step flow
- `intake/persona_selector.py` — exports `PERSONAS: dict` with persona metadata
- `intake/topic_intake.py` — exports `build_research_brief(...) -> ResearchBrief`
- `source_engine/discovery.py` — exports `discover_sources(brief) -> List[Dict]`

**Squad 3 (Content Creator crew):**
- `crews/content_creator/crew.py` — exports `ContentCreatorCrew(BaseCrew)`

**Squad 4 (Product Manager crew):**
- `crews/product_manager/crew.py` — exports `ProductManagerCrew(BaseCrew)`

**Squad 5 (Bharat Desha crew — DONE):**
- `crews/bharat_desha/crew.py` — exports `BharatDeshaCrew(BaseCrew)`

---

## Integration points

### 1. Crew router (`crews/router.py`)

New file. Single responsibility: map persona string → crew instance.

```python
CREW_MAP = {
    "content_creator": ContentCreatorCrew,
    "product_manager": ProductManagerCrew,
    "bharat_desha": BharatDeshaCrew,
}

def get_crew(persona: str) -> BaseCrew:
    ...
```

### 2. Persona registry update (`intake/persona_selector.py`)

Add Bharat Desha entry with its artifact options:
```python
"bharat_desha": {
    "label": "Bharat Desha",
    "description": "Spiritual India travel content — itineraries, destination guides, Sanatan Dharma, wellness, and social media repurposing.",
    "artifacts": ["blog_post", "itinerary", "destination_guide", "wellness_guide", "instagram", "facebook", "x_post", "youtube"],
    "always_included": ["seo_keywords"],
}
```

### 3. Artifact renderer (`app.py` or `ui/artifact_renderer.py`)

Must handle all artifact types across all personas:
- `blog_post`, `itinerary`, `destination_guide`, `wellness_guide` → markdown display
- `instagram`, `facebook`, `x_post` → copyable text box with platform label
- `youtube` → sections: Title, Description, Chapters
- `seo_keywords` → numbered list display
- `content_brief`, `competitive_analysis`, `product_roadmap` etc. (Squad 3/4 artifacts) → markdown

### 4. LangFuse session wiring

`app.py` generates a `session_id = str(uuid4())` at the start of each research run and passes it to `get_langfuse_handler(session_id)`. The handler is available to crew runs via Streamlit session state.

### 5. LanceDB table isolation

Each crew must write to its own table:
- Content Creator → `content_creator`
- Product Manager → `product_manager`
- Bharat Desha → `bharat_desha` (already set via `config.BHARAT_DESHA_TABLE`)

---

## Out of scope

- Docker / production deploy (Task 21)
- Any new agent logic
- UI redesign
- Performance optimisation
