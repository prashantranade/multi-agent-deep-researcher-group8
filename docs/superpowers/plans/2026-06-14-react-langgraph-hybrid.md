# Hybrid ReAct + LangGraph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

> **Status:** **COMPLETE** — Phases 0–9 implemented and verified (2026-06-14).

**Goal:** LLM-driven tool selection via LangChain `@tool` docstrings, orchestrated by LangGraph for phase order, retries, and parallel artifact generation.

**Architecture:** LangGraph outer graph controls retrieve → analyse → generate phases. Each phase node runs a LangChain `create_react_agent` subgraph where the LLM reads tool docstrings and picks tools. Tools delegate to existing agent classes.

**Tech Stack:** LangGraph 0.2.x, LangChain 0.2.x, `langchain-openai`, `create_react_agent`, Langfuse 3.x, pytest.

**Design spec:** `docs/superpowers/specs/2026-06-14-react-langgraph-hybrid-design.md`

---

## Execution order

```
Phase 0: llm_factory.py                    ✅
Phase 1: graph_state + graph_utils         ✅
Phase 2: crews/tools/cc_tools.py           ✅
Phase 3: crews/react/ ReAct runners        ✅
Phase 4: content_creator/graph.py          ✅
Phase 5: ContentCreatorCrew.run()          ✅
Phase 6: Product Manager                   ✅
Phase 7: Bharat Desha                      ✅
Phase 8: LangFuse callbacks                ✅
Phase 9: Docs + full verification          ✅
```

---

## Architecture (all personas)

```
app.py → get_crew(persona) → crew.run(brief, session_id=...)
                │
                ▼
        invoke_crew_graph()  [LangFuse callbacks optional]
                │
                ▼
        LANGGRAPH StateGraph
        [trend/seo for BD] → retrieve → analyse → [retry | generate]
                │
                ▼ (each ReAct phase node)
        create_react_agent (LangChain)
        LLM reads @tool docstrings → ToolNode
                │
                ▼
        Existing persona agents (retrieval / analysis / output)
```

---

## Persona summary

| Persona | Graph | ReAct phases | Special nodes | LanceDB table |
|---------|-------|--------------|---------------|---------------|
| `content_creator` | `crews/content_creator/graph.py` | retrieve, analyse, generate | parallel `Send` per artifact | `cc_research` |
| `product_manager` | `crews/product_manager/graph.py` | retrieve, analyse, generate | parallel `Send` per artifact | `pm_research` |
| `bharat_desha` | `crews/bharat_desha/graph.py` | retrieve, analyse, generate | fixed `trend` + `seo` upstream | `bharat_desha` |

All crews expose `run(brief, *, session_id=None, user_id="anonymous") → CrewOutput(artifacts, trace_id)`.

`BaseCrew.retrieve()` / `analyse()` / `generate_artifacts()` remain for direct agent access and tests.

---

## Verification (Phase 9)

**Date verified:** 2026-06-14  
**Result:** `106 passed`, 1 deprecation warning (LangGraph checkpoint serializer — upstream)

### Commands

```bash
# Full suite
python -m pytest -q

# Hybrid / crew subset
python -m pytest tests/test_cc_graph.py tests/test_pm_graph.py tests/test_bd_graph.py \
  tests/test_cc_tools.py tests/test_pm_tools.py tests/test_bd_tools.py \
  tests/test_cc_react.py tests/test_graph_invoke.py tests/test_langfuse_client.py \
  tests/test_cc_e2e.py tests/test_pm_e2e.py tests/test_bharat_desha_crew.py \
  tests/test_crew_router.py -q

# Streamlit (suppress torchvision watcher noise)
streamlit run app.py --server.fileWatcherType none
```

### Checklist

| Area | Verified by |
|------|-------------|
| LLM factory (OpenRouter + fallback) | `test_llm_factory.py` |
| Shared graph state + retry routing | `test_graph_state.py`, `test_*_graph.py` |
| CC / PM / BD LangChain tools | `test_cc_tools.py`, `test_pm_tools.py`, `test_bd_tools.py` |
| ReAct runner + config propagation | `test_cc_react.py` |
| LangGraph pipelines (mock ReAct) | `test_cc_graph.py`, `test_pm_graph.py`, `test_bd_graph.py` |
| Crew `run()` → graph + LangFuse hook | `test_*_e2e.py`, `test_bharat_desha_crew.py`, `test_graph_invoke.py` |
| Router (all 3 personas) | `test_crew_router.py` |
| LangFuse client (opt-in tracing) | `test_langfuse_client.py` |
| Legacy agent unit tests | `test_cc_*`, `test_pm_*`, `test_bharat_desha_crew.py` (agent-level) |

### Environment

Requires `.env.local` (or `.env`) with at least:

```
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...
```

Optional (LangFuse tracing in Step 7):

```
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Out of scope (post-hackathon)

- LLM-driven persona selection (user still picks in Streamlit Step 1)
- Replacing agent classes with pure LCEL chains (Option C)
- Bharat Desha in Streamlit Step 1 persona radio (router supports it; UI not wired)
