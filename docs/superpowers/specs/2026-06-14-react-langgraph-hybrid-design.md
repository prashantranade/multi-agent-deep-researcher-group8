# Hybrid ReAct + LangGraph — Design Spec

**Date:** 2026-06-14  
**Status:** **COMPLETE** — Phases 0–9 (all crews, LangFuse, verified)

## Summary

Content Creator, Product Manager, and Bharat Desha crews use **LangGraph** for phase orchestration and **LangChain ReAct agents** inside retrieval/analyse/generate phases so the LLM selects tools via docstrings. Bharat Desha adds fixed upstream **trend** and **seo** nodes before ReAct phases. All graph invocations go through **`invoke_crew_graph()`** with optional LangFuse tracing.

## Layer responsibilities

| Layer | Role |
|-------|------|
| **app.py / router** | User picks persona; `get_crew()` → crew class |
| **invoke_crew_graph** | LangFuse callbacks, session propagation, trace_id extraction |
| **LangGraph** | Fixed phases, analysis retry, parallel `Send` (CC/PM) or sequential generate (BD) |
| **LangChain ReAct** | `create_react_agent` + `@tool` docstrings per phase |
| **Tools** | Wrap existing retrieval / analysis / output agents per persona |
| **ToolRuntime** | `contextvars` passes `ResearchBrief`, `db_path`, trend/seo context into tools |
| **LangFuse** | `CallbackHandler` on `graph.invoke`; config propagated to nested ReAct via contextvar |

## Observability

```
app.py session_id → crew.run(brief, session_id=...)
  → invoke_crew_graph(graph, state)
    → Langfuse CallbackHandler in graph.invoke(config={"callbacks": [...]})
    → propagate_attributes(session_id, user_id, metadata)
    → contextvar propagates config to run_react_phase (nested LLM spans)
  → CrewOutput(trace_id=handler.last_trace_id)
```

Tracing is opt-in: skipped when `LANGFUSE_SECRET_KEY` / `LANGFUSE_PUBLIC_KEY` are unset.

## Content Creator graph

```
START → react_retrieve → react_analyse ──(valid)──► Send × N react_generate → END
                              │ retry / fail
                              └──► increment_retry / analysis_failed
```

**Analysis validator:** `is_valid_cc_analysis` — requires `trends` or `hooks`.

## Product Manager graph

Same shape as Content Creator. **Analysis validator:** `is_valid_pm_analysis` — `market_size != "unknown"` or has `competitors`.

## Bharat Desha graph

```
START → trend → seo → react_retrieve → react_analyse ──(valid)──► react_generate → END
                                           │ retry / fail
                                           └──► increment_retry / analysis_failed
```

Fixed nodes: `trend`, `seo`. Generate always includes `seo_keywords`; primary content then social repurposing.

**Analysis validator:** `is_valid_bd_analysis` — requires `spiritual` or `key_points`.

## ReAct tools by persona

### Content Creator

| Tool | Purpose |
|------|---------|
| `scrape_and_index_sources` | Scrape URLs, embed into LanceDB |
| `search_research_chunks` | Semantic search over index |
| `analyse_content_strategy` | LLM analysis → JSON |
| `generate_content_artifact` | One artifact from analysis |

### Product Manager

| Tool | Purpose |
|------|---------|
| `scrape_and_index_market_sources` | Scrape URLs, embed into `pm_research` |
| `search_market_research_chunks` | Semantic search over PM index |
| `analyse_market_strategy` | Market analysis JSON |
| `generate_pm_artifact` | One PM artifact from analysis |

### Bharat Desha

| Tool | Purpose |
|------|---------|
| `search_and_index_travel_research` | Tavily + LanceDB `bharat_desha` |
| `analyse_bharat_desha_research` | Spiritual/practical/cultural JSON |
| `generate_primary_travel_content` | blog / itinerary / guide / wellness |
| `generate_social_travel_content` | instagram / facebook / x_post / youtube |

## Key files

```
observability/langfuse_client.py      # Langfuse 3.x CallbackHandler, build_graph_invoke_config
crews/graph_invoke.py                 # invoke_crew_graph(), run-config contextvar
infrastructure/llm_factory.py         # make_llm() for ReAct
crews/graph_state.py                  # CrewGraphState, make_initial_state()
crews/graph_utils.py                  # analysis validators, retry nodes
crews/tools/tool_context.py         # ToolRuntime (brief, db_path, trend/seo, artifacts)
crews/tools/{cc,pm,bd}_tools.py       # @tool definitions per persona
crews/react/runner.py                 # run_react_phase() — create_react_agent
crews/react/{cc,pm,bd}_prompts.py     # phase system prompts
crews/{content_creator,product_manager,bharat_desha}/graph.py
crews/{content_creator,product_manager,bharat_desha}/crew.py
crews/router.py                       # get_crew(persona)
app.py                                # Step 7: crew.run(brief, session_id=...)
```

## Verification record

| Metric | Value |
|--------|-------|
| Test suite | `106 passed` |
| Hybrid-specific tests | 26 test modules under `tests/` |
| Verified date | 2026-06-14 |
| Command | `python -m pytest -q` |

See `docs/superpowers/plans/2026-06-14-react-langgraph-hybrid.md` for full checklist and run commands.
