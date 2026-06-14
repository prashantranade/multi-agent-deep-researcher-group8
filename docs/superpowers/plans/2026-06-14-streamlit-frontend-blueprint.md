# Streamlit UI — Implementation Blueprint

**Date:** 2026-06-14  
**Status:** Implemented (2026-06-14)  
**Design source:** [`docs/superpowers/specs/2026-06-14-streamlit-frontend-design.md`](../specs/2026-06-14-streamlit-frontend-design.md)  
**Enhancements:** Living dossier (steps 1–6) + Agent theater (step 7) from design review

---

## 1. Blueprint overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HEADER — hero thesis · session_id (mono) · trace_id when available     │
├──────────┬──────────────────────┬───────────────────────────────────────┤
│  SPINE   │  DOSSIER (live)      │  WORKSPACE (single active step)       │
│  200px   │  280px               │  flex                                 │
│          │                      │                                       │
│  Phase   │  Research file       │  Inputs · actions · step copy         │
│  nav     │  builds as user      │                                       │
│          │  progresses          │                                       │
└──────────┴──────────────────────┴───────────────────────────────────────┘
                              ↓ step 7 only
┌─────────────────────────────────────────────────────────────────────────┐
│  AGENT THEATER — persona pipeline diagram + status + deliverable cards  │
└─────────────────────────────────────────────────────────────────────────┘
```

| Layer | Responsibility |
|-------|----------------|
| `app.py` | Page config, session init, column shell, dispatch active step |
| `ui/theme.py` | CSS variables, font injection, Streamlit overrides |
| `ui/components.py` | Reusable HTML/CSS building blocks |
| `ui/dossier.py` | Live brief preview from `session_state` |
| `ui/spine.py` | Phase navigation + completion state |
| `ui/agent_theater.py` | Step 7 pipeline visualization |
| `ui/steps/*.py` | One module per step — logic migrated from current `app.py` |
| `ui/constants.py` | Phase labels, persona metadata, artifact catalogs |

**Non-goals:** Change crew/graph logic, session state keys (except optional `view_step` for spine revisit), or pytest targets.

---

## 2. Design tokens → CSS variables

Inject once at app start via `ui/theme.py`:

```css
:root {
  --dr-paper: #f5f6f2;
  --dr-surface: #ffffff;
  --dr-ink: #141820;
  --dr-ink-muted: #5c6570;
  --dr-border: #dde3ea;
  --dr-forest: #2d5a4a;
  --dr-forest-hover: #3d7a66;
  --dr-highlight: #e8f0ec;
  --dr-score-high: #2d5a4a;
  --dr-score-mid: #8a6914;
  --dr-score-low: #8b4049;
  --dr-error: #9b2c2c;
  --dr-radius: 6px;
  --dr-space-1: 8px;
  --dr-space-2: 16px;
  --dr-space-3: 24px;
  --dr-space-4: 32px;
  --dr-font-display: 'Bitter', Georgia, serif;
  --dr-font-body: 'Atkinson Hyperlegible', system-ui, sans-serif;
  --dr-font-mono: 'IBM Plex Mono', monospace;
}
```

### `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#2d5a4a"
backgroundColor = "#f5f6f2"
secondaryBackgroundColor = "#ffffff"
textColor = "#141820"
font = "sans serif"

[server]
headless = true

[browser]
gatherUsageStats = false
```

---

## 3. Session state contract

| Key | Type | Set at step | Used by |
|-----|------|-------------|---------|
| `session_id` | `str` | init | LangFuse, header |
| `step` | `int` 1–7 | navigation | spine, dispatch |
| `view_step` | `int` optional | spine click | read-only revisit (≤ `step`) |
| `persona` | `str` | 1 | dossier, artifacts, crew |
| `topic` | `str` | 2 | dossier, discovery |
| `context_text` | `str` | 3 | clarification |
| `answers` | `dict` | 4 | clarification |
| `brief` | `ResearchBrief` | 4 end | crew, dossier |
| `sources` | `list[dict]` | 4 end | step 5 |
| `artifacts` | `list[dict]` | 7 | results |
| `trace_id` | `str` optional | 7 | header |

**Step → spine label mapping**

| `step` | Spine label | Module |
|--------|-------------|--------|
| 1 | Persona | `ui/steps/persona.py` |
| 2 | Topic | `ui/steps/topic.py` |
| 3 | Context | `ui/steps/context.py` |
| 4 | Clarify | `ui/steps/clarify.py` |
| 5 | Sources | `ui/steps/sources.py` |
| 6 | Outputs | `ui/steps/outputs.py` |
| 7 | Deliverables | `ui/steps/results.py` |

---

## 4. File tree (target)

```
app.py
.streamlit/config.toml
ui/
├── __init__.py
├── constants.py          # PHASES, PERSONAS, ARTIFACT_OPTIONS
├── theme.py              # inject_theme()
├── styles.css            # loaded by theme.py
├── components.py         # render_* HTML helpers
├── spine.py              # render_spine(step, view_step)
├── dossier.py            # render_dossier(session_state)
├── agent_theater.py      # render_pipeline(persona, phase_status)
└── steps/
    ├── __init__.py
    ├── persona.py        # render_step_persona()
    ├── topic.py
    ├── context.py
    ├── clarify.py
    ├── sources.py
    ├── outputs.py
    └── results.py
```

---

## 5. `app.py` orchestration (pseudocode)

```python
def main():
    init_session_state()
    inject_theme()

    render_header()  # hero + session + trace

    if st.session_state.step == 7:
        # Full-width agent theater layout
        render_step_results()
        return

    col_spine, col_dossier, col_work = st.columns([0.15, 0.22, 0.63])

    with col_spine:
        view = render_spine(st.session_state.step, st.session_state.get("view_step"))

    with col_dossier:
        render_dossier(st.session_state)

    with col_work:
        active = view or st.session_state.step
        STEP_RENDERERS[active]()  # only one step UI mounted

if __name__ == "__main__":
    main()
```

**Mobile (`st.session_state` or CSS media query):** hide dossier column; spine → horizontal stepper via `components.py` + `@media (max-width: 768px)`.

---

## 6. Component specifications

### 6.1 `render_header()`

```
┌────────────────────────────────────────────────────────────┐
│ Deep Researcher                                    [mono]  │
│ Build a source-verified brief, then run your agent crew.   │
│ session a3f2… · trace (if set)                             │
└────────────────────────────────────────────────────────────┘
```

- Title: Bitter, `--dr-font-display`, 2rem
- Thesis: body, `--dr-ink-muted`
- IDs: `--dr-font-mono`, 0.8rem

### 6.2 `render_spine(current, view_step)`

HTML nav with three states per phase:

| State | Style |
|-------|--------|
| upcoming | `ink-muted`, hollow circle |
| active | `forest` text, `--dr-highlight` bg, filled dot |
| complete | checkmark, clickable → sets `view_step` |

Each item is `st.button` with `key=f"spine_{i}"` + custom CSS class, or pure HTML + link buttons.

**Read-only revisit:** when `view_step < step`, workspace shows summary component, not edit form.

### 6.3 `render_dossier(state)` — Living dossier

Sticky card listing fields as they become known:

```
RESEARCH FILE
─────────────
Lens:     Content creator
Topic:    Sustainable travel in Rajasthan
Audience: Millennials          ← from answers
Tone:     Inspirational
Depth:    Standard
Context:  ✓ URL added
Sources:  4 selected
Outputs:  content_brief, captions
Status:   Ready to run
```

- Empty fields show em dash `—` in muted mono
- Checkmarks for optional context when non-empty
- Subtle typewriter-style CSS transition on field update (respect `prefers-reduced-motion`)

### 6.4 `render_persona_cards()`

Three cards in `st.columns(3)`:

| `persona` key | Title | Promise | Accent border when selected |
|---------------|-------|---------|----------------------------|
| `content_creator` | Content creator | Hooks, captions, social drafts | `forest` |
| `product_manager` | Product manager | Market + PRD insights | `forest` |
| `bharat_desha` | Bharat Desha | SEO travel + trend intel | `forest` |

Selection: `st.session_state.persona` set on card click (radio pattern via buttons).

### 6.5 `render_source_card(src, selected)`

```
┌─────────────────────────────────────────────┐
│ [✓]  Sustainable Rajasthan Travel Guide     │
│      example.com · 2025-01-01               │
│      ████████████░░░░  82% confidence       │
└─────────────────────────────────────────────┘
```

- Bar color from score: high / mid / low tokens
- Checkbox remains Streamlit native (hidden label; card click toggles)

### 6.6 `render_artifact_chips(persona, selected)`

Multiselect replaced with toggle chips (button group styled via CSS). Options from `ui/constants.py`:

```python
ARTIFACT_OPTIONS = {
    "content_creator": [
        ("content_brief", "Content brief"),
        ("social_draft", "Social draft"),
        ...
    ],
    "product_manager": [...],
    "bharat_desha": [
        ("blog_post", "Blog post"),
        ("seo_keywords", "SEO keywords (always included)"),
        ...
    ],
}
```

### 6.7 `render_agent_theater(persona)` — Step 7 signature

**Static pipeline diagrams** (honest — not fake live streaming unless wired later):

| Persona | Pipeline nodes shown |
|---------|---------------------|
| `content_creator` | Retrieve → Analyse → Generate × N |
| `product_manager` | Retrieve → Analyse → Generate × N |
| `bharat_desha` | Trend → SEO → Retrieve → Analyse → Generate |

During `crew.run()`:

1. Show pipeline with all nodes `pending`
2. Spinner + copy: *"Running research crew (30–60 seconds)…"*
3. On complete: mark all nodes `complete`; reveal deliverable cards below

**Future enhancement (v2):** stream LangGraph node events into theater — not required for v1 blueprint.

### 6.8 `render_artifact_panel(artifact)`

```
┌─ Content Brief ─────────────────── [Download .md] ─┐
│  Styled markdown body (Bitter h1, body Atkinson)   │
└────────────────────────────────────────────────────┘
```

- Wrap exported markdown in `.dr-artifact` container
- Download button: primary `forest` styling

---

## 7. Step-by-step workspace specs

### Step 1 — Persona (`persona.py`)

| Element | Spec |
|---------|------|
| Phase title | "Choose your lens" |
| Body | Persona cards (3) |
| Primary CTA | "Continue to topic" — disabled until persona selected |
| On submit | `step = 2`, `rerun()` |

### Step 2 — Topic (`topic.py`)

| Element | Spec |
|---------|------|
| Phase title | "What do you want to research?" |
| Input | Large text input, placeholder from design spec |
| CTA | "Continue to context" |

### Step 3 — Context (`context.py`)

| Element | Spec |
|---------|------|
| Phase title | "Bring your materials" |
| Subcopy | "Optional — URL, handle, or documents" |
| Inputs | URL, handle, file uploader (existing enrichment logic) |
| CTA | "Continue to clarify" / "Skip for now" |

### Step 4 — Clarify (`clarify.py`)

| Element | Spec |
|---------|------|
| Phase title | "Sharpen your brief" |
| Progress | "Question {n} of {total}" |
| Input | Single question from `ClarificationAgent` |
| CTA | "Next" / "Discover sources" when complete |
| Side effect | On discover: build brief, Tavily discovery, `step = 5` |

### Step 5 — Sources (`sources.py`)

| Element | Spec |
|---------|------|
| Phase title | "Curate your sources" |
| Subcopy | "Scored by recency, authority, relevance" |
| List | `render_source_card` per source |
| CTA | "Confirm sources" — requires ≥ 1 selected |

### Step 6 — Outputs (`outputs.py`)

| Element | Spec |
|---------|------|
| Phase title | "Choose deliverables" |
| UI | Artifact chips for current persona |
| CTA | "Run research crew" → `step = 7` |

### Step 7 — Deliverables (`results.py`)

| Element | Spec |
|---------|------|
| Layout | Full width — no spine/dossier columns |
| Run | Agent theater + spinner → `crew.run(brief, session_id=...)` |
| Output | Artifact panels + downloads |
| Footer | Trace ID caption, "Start new research" |

---

## 8. Persona → backend mapping

Unchanged from `crews/router.py`:

```python
PERSONA_TO_CREW = {
    "content_creator": ContentCreatorCrew,
    "product_manager": ProductManagerCrew,
    "bharat_desha": BharatDeshaCrew,
}
```

Step 6 must include `bharat_desha` artifact list (see Bharat Desha design spec).

---

## 9. CSS hook classes

| Class | Target |
|-------|--------|
| `.dr-app` | Root wrapper |
| `.dr-header` | Top bar |
| `.dr-spine` | Left nav |
| `.dr-spine__item--active` | Current phase |
| `.dr-spine__item--done` | Completed phase |
| `.dr-dossier` | Live brief card |
| `.dr-dossier__field` | Label + value row |
| `.dr-workspace` | Main panel |
| `.dr-persona-card` | Persona selector |
| `.dr-persona-card--selected` | Selected state |
| `.dr-source-card` | Source row |
| `.dr-confidence-bar` | Score bar track/fill |
| `.dr-chip` | Artifact toggle |
| `.dr-chip--on` | Selected artifact |
| `.dr-pipeline` | Agent theater |
| `.dr-pipeline__node--pending/active/done` | Node states |
| `.dr-artifact` | Result markdown container |

Streamlit overrides (examples):

```css
.stButton > button[kind="primary"] {
  background-color: var(--dr-forest);
  border-radius: var(--dr-radius);
}
div[data-testid="stTextInput"] input {
  border-color: var(--dr-border);
}
```

---

## 10. Implementation sequence

```
A. Foundation
   ├── .streamlit/config.toml
   ├── ui/theme.py + styles.css
   └── app.py shell (header + columns, no steps yet)

B. Navigation
   ├── ui/constants.py (PHASES)
   ├── ui/spine.py
   └── ui/dossier.py

C. Steps 1–3
   ├── persona.py (cards + BD)
   ├── topic.py
   └── context.py

D. Steps 4–6
   ├── clarify.py
   ├── sources.py (confidence bars)
   └── outputs.py (chips + BD artifacts)

E. Step 7
   ├── agent_theater.py
   └── results.py (artifact panels)

F. Polish
   ├── Mobile stepper CSS
   ├── prefers-reduced-motion
   ├── focus-visible
   └── Manual browser QA

G. Verify
   └── python -m pytest -q  (must stay 106 passed)
```

---

## 11. Acceptance checklist

- [x] Reading Room palette applied globally
- [x] Three-column shell on desktop; stepper on mobile
- [x] Dossier updates live across steps 1–6
- [x] Single workspace panel (no expander stack)
- [x] All three personas + artifact sets
- [x] Source confidence bars with token colors
- [x] Step 7 agent theater + styled deliverables
- [x] LangFuse trace in header when present
- [x] pytest suite green (106 passed)
- [x] Design spec success criteria met

---

## 12. Related documents

| Doc | Role |
|-----|------|
| [Streamlit frontend design](../specs/2026-06-14-streamlit-frontend-design.md) | Vision, tokens, voice |
| [Hybrid crew architecture](../specs/2026-06-14-react-langgraph-hybrid-design.md) | Agent pipelines for theater |
| [Bharat Desha persona](../specs/2026-06-13-bharat-desha-persona-design.md) | BD artifacts + flow |
