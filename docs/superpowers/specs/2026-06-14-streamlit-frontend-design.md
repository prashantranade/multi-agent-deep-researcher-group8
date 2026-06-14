# Streamlit App — Frontend Design Plan

**Date:** 2026-06-14  
**Status:** Implemented  
**Blueprint:** [`docs/superpowers/plans/2026-06-14-streamlit-frontend-blueprint.md`](../plans/2026-06-14-streamlit-frontend-blueprint.md)  
**Skill basis:** `.agents/skills/frontend-design`  
**Target:** `app.py` (Multi-Agent Deep Researcher, 7-step intake → crew run → artifacts)

---

## 1. Product grounding

| Dimension | Choice |
|-----------|--------|
| **Subject** | A guided **research session** — from vague topic to source-verified deliverables produced by persona-specific agent crews |
| **Audience** | Content creators and product managers (demo/hackathon users) who need to **trust sources** and **pick outputs**, not chat casually |
| **Single job** | *“Take my topic through a structured brief, let me curate evidence, then run the right agent crew and give me downloadable artifacts.”* |
| **Vernacular** | Briefs, sources, confidence scores, citations, agent runs, trace IDs, artifacts — the language of **editorial research**, not generic SaaS dashboards |

The 7 steps are a **real sequential pipeline** (not decorative numbering). Structure should encode that sequence, but the UI should show **one active phase at a time**, not seven stacked accordions.

---

## 2. Current state audit

| Issue | Why it hurts |
|-------|----------------|
| Default Streamlit chrome + expanders for every step | Feels like a settings form, not a research session |
| All steps visible once unlocked | Cognitive load; past steps compete with the current task |
| Generic title + caption | No thesis; doesn’t communicate “source-verified multi-agent research” |
| Persona as plain radio | Misses opportunity to explain *what changes* per crew |
| Source list = checkbox wall | Scores are secondary; trust signals should lead |
| Step 7 = markdown dump | Artifacts deserve typographic treatment and clear download affordances |
| Bharat Desha missing from Step 1 | Router supports it; UI does not |

**Keep (behavior, not layout):** session state machine, clarification loop, source scoring, crew router, LangFuse `trace_id`, artifact export.

---

## 3. Design direction: **Reading Room**

**Concept:** A calm **reading room / research desk** — daylight, paper surfaces, ink text, forest-green actions. Evokes institutional credibility (library, field notes) without dark-mode hacker aesthetic or warm “AI startup cream.”

### Anti-patterns explicitly avoided

| AI-default look | Our choice instead |
|-----------------|-------------------|
| Warm cream `#F4F1EA` + terracotta serif | Cool paper `#f5f6f2` + blue-black ink |
| Near-black + acid green accent | Light surfaces + deep forest green actions |
| Broadsheet hairline newspaper | Card-based sources with confidence as **signal**, not decoration |
| Gradient hero + big stat numbers | Text-led hero: one line on *what this session will produce* |
| Seven open expanders | **Source spine** + single active panel |

### One aesthetic risk (justified)

**Source spine navigation** — a persistent left rail listing the seven pipeline phases with completion state. Risk: sidebar real estate in Streamlit. Payoff: the product *is* a pipeline; the spine makes progress legible and replaces accordion clutter. Completed phases collapse to a single-line summary in the main panel when revisiting is needed.

---

## 4. Design tokens

### Color

| Token | Hex | Role |
|-------|-----|------|
| `paper` | `#f5f6f2` | App background |
| `surface` | `#ffffff` | Cards, inputs, artifact panels |
| `ink` | `#141820` | Primary text |
| `ink-muted` | `#5c6570` | Captions, helper copy |
| `border` | `#dde3ea` | Dividers, card edges |
| `forest` | `#2d5a4a` | Primary buttons, active spine node |
| `forest-hover` | `#3d7a66` | Hover / focus ring |
| `highlight` | `#e8f0ec` | Active panel wash |
| `score-high` | `#2d5a4a` | Source confidence ≥ 70% |
| `score-mid` | `#8a6914` | 40–69% |
| `score-low` | `#8b4049` | &lt; 40% |
| `error` | `#9b2c2c` | Agent failures |
| `success` | `#2d5a4a` | Brief complete, step done |

### Typography (Google Fonts via CSS injection)

| Role | Face | Fallback | Usage |
|------|------|----------|--------|
| **Display** | [Bitter](https://fonts.google.com/specimen/Bitter) | Georgia, serif | Page title, phase headings, artifact titles |
| **Body** | [Atkinson Hyperlegible](https://fonts.google.com/specimen/Atkinson+Hyperlegible) | system-ui, sans | Labels, questions, body copy |
| **Data** | [IBM Plex Mono](https://fonts.google.com/specimen/IBM+Plex+Mono) | monospace | Domains, dates, scores, trace IDs, artifact keys |

### Type scale

| Level | Size | Weight | Face |
|-------|------|--------|------|
| Hero | 2rem | 600 | Bitter |
| Phase title | 1.35rem | 600 | Bitter |
| Section | 1rem | 600 | Atkinson |
| Body | 0.95rem | 400 | Atkinson |
| Caption | 0.8rem | 400 | Atkinson, `ink-muted` |
| Data | 0.85rem | 500 | Plex Mono |

### Spacing & shape

- Base unit: **8px** (8, 16, 24, 32, 48)
- Card radius: **6px** (subtle, not pill-heavy)
- Max content width: **720px** in main panel (readable line length for questions)
- Wide layout: spine **220px** + fluid main

---

## 5. Layout wireframes

### Global shell

```
┌──────────────────────────────────────────────────────────────────┐
│  ◉ Deep Researcher          research session · trace (mono)      │
│  Persona-aware · source-verified · multi-agent                   │
├─────────────┬────────────────────────────────────────────────────┤
│ SOURCE SPINE│  MAIN PANEL (one phase active)                     │
│             │                                                    │
│ ● Brief     │  ┌─ Phase header ─────────────────────────────┐   │
│ ○ Context   │  │  Clarify your brief                        │   │
│ ○ Clarify   │  │  One question at a time…                   │   │
│ ○ Sources   │  └────────────────────────────────────────────┘   │
│ ○ Outputs   │                                                    │
│ ○ Run       │  [ question input ]                                │
│ ○ Results   │  [ Continue ]                                      │
│             │                                                    │
└─────────────┴────────────────────────────────────────────────────┘
```

Legend: `●` active · `◉` complete · `○` upcoming

### Phase-specific notes

| Phase | Panel focus |
|-------|-------------|
| **Brief** (persona + topic) | Persona cards (3-up grid on wide); topic as large single input |
| **Context** | Optional URL / handle / upload grouped as “Bring your materials” |
| **Clarify** | One question per screen; progress “Question 2 of 4” |
| **Sources** | Card per source: title, domain (mono), date, confidence bar |
| **Outputs** | Artifact chips by persona; short description per type |
| **Run** | Full-width status: agent phase names, elapsed time, spinner copy |
| **Results** | Tab or accordion per artifact; styled markdown; download prominent |

### Mobile (&lt; 768px)

Spine becomes **horizontal stepper** at top (compact dots + labels); main panel full width.

---

## 6. Signature element: **Source spine**

The left rail (or top stepper on mobile) is the memorable element:

- Phase names encode **research language**: `Persona` → `Topic` → `Context` → `Clarify` → `Sources` → `Outputs` → `Deliverables`
- Completed steps show a small check; active step uses `forest` + `highlight` wash
- Clicking a **completed** step opens a read-only summary in main panel (not re-editing by default)

This replaces seven Streamlit expanders with one navigation metaphor tied to the product.

---

## 7. Copy & voice

| Principle | Example |
|-----------|---------|
| User-facing names, not system names | “Choose your lens” not “Select persona enum” |
| Active buttons | “Continue to topic”, “Find sources”, “Run research crew” |
| Errors are actionable | “Research crew failed: check API keys in `.env.local`” + which step failed |
| Empty sources | “No sources yet — we’ll search once your brief is complete.” |
| Run spinner | “Retrieving sources → analysing → generating artifacts (30–60s)” |

**Hero line (thesis):**  
*“Build a source-verified research brief, then let your agent crew produce the artifacts you choose.”*

---

## 8. Persona presentation

Replace horizontal radio with **persona cards**:

| Persona | Label | One-line promise |
|---------|-------|------------------|
| `content_creator` | Content creator | Hooks, captions, and social-ready drafts from curated sources |
| `product_manager` | Product manager | Market signals, competition, and PRD-ready insights |
| `bharat_desha` | Bharat Desha | SEO travel content with trend + keyword intelligence |

Each card: icon placeholder (CSS), title, promise, subtle border; selected = `forest` border + `highlight` fill.

---

## 9. Streamlit implementation approach

### File structure (proposed)

```
app.py                          # Thin orchestrator: session + step routing
ui/
├── __init__.py
├── theme.py                    # inject_css(), load_google_fonts()
├── styles.css                  # Token-based overrides for Streamlit classes
├── components.py               # spine, persona_card, source_card, artifact_panel
└── steps/
    ├── __init__.py
    ├── persona.py
    ├── topic.py
    ├── context.py
    ├── clarify.py
    ├── sources.py
    ├── outputs.py
    └── results.py
.streamlit/config.toml          # base theme aligned to tokens (primaryColor, backgroundColor)
```

### Technical tactics

1. **`st.markdown(inject_css(), unsafe_allow_html=True)`** once at top — fonts, CSS variables, Streamlit widget overrides (`stButton`, `stTextInput`, `[data-testid="stSidebar"]` if used).
2. **`layout="wide"`** + `st.columns([1, 4])` for spine + main (desktop).
3. **Single active step render** — only call the active step module; spine reads `st.session_state.step`.
4. **`st.session_state` unchanged** — design is presentation-only; no crew/graph changes in this pass.
5. **Reduced motion** — `@media (prefers-reduced-motion: reduce)` disables spine transitions.
6. **Focus** — visible `:focus-visible` outlines using `forest-hover`.

### Streamlit limitations (accepted)

- Cannot fully remove Streamlit header/footer without hacks; theme minimization only.
- Custom fonts require network (Google Fonts CDN) or bundled WOFF later.
- Spine “click to revisit” may use buttons styled as nav links.

---

## 10. Implementation phases

| Phase | Scope | Est. |
|-------|--------|------|
| **A** | `ui/theme.py`, `.streamlit/config.toml`, base CSS tokens | Small |
| **B** | Source spine + step router refactor in `app.py` | Medium |
| **C** | Persona cards + Bharat Desha in Step 1 | Small |
| **D** | Source cards with confidence bars | Medium |
| **E** | Results / artifact panels + download styling | Medium |
| **F** | Mobile stepper + accessibility pass | Small |
| **G** | Manual QA in browser + screenshot critique | Small |

**Out of scope for v1 redesign:** custom logo SVG, animation beyond CSS transitions, dark mode toggle.

---

## 11. Success criteria

- [ ] Only **one primary task** visible per screen (no seven open expanders)
- [ ] Palette and typography **distinct from** cream/terracotta and dark/acid-green defaults
- [ ] Source confidence **scannable** at a glance
- [ ] All three personas selectable including **Bharat Desha**
- [ ] LangFuse trace ID visible but unobtrusive (mono caption)
- [ ] Existing **106 pytest tests** still pass (UI refactor must not break crew logic)
- [ ] Readable at 375px width; keyboard navigable

---

## 12. Review checklist (pre-build)

Before coding, confirm with stakeholder:

1. **Direction “Reading Room”** — cool paper + forest green — acceptable for hackathon demo?
2. **Bharat Desha** in persona step — include in this redesign?
3. **Spine navigation** — worth the Streamlit column tradeoff?
4. **Google Fonts CDN** — ok for offline/restricted networks, or bundle fonts?

---

## Related docs

- **Implementation blueprint:** `docs/superpowers/plans/2026-06-14-streamlit-frontend-blueprint.md`
- Product architecture: `docs/superpowers/plans/2026-06-13-deep-researcher.md`
- Crew graphs: `docs/superpowers/specs/2026-06-14-react-langgraph-hybrid-design.md`
- Bharat Desha persona: `docs/superpowers/specs/2026-06-13-bharat-desha-persona-design.md`
