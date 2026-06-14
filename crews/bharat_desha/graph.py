from langgraph.graph import StateGraph, START, END

from crews.graph_state import CrewGraphState
from crews.graph_utils import (
    analysis_route,
    increment_retry_node,
    analysis_failed_node,
    is_valid_bd_analysis,
)
from crews.tools.tool_context import ToolRuntime, set_runtime, reset_runtime
from crews.tools.bd_tools import (
    BD_RETRIEVE_TOOLS,
    BD_ANALYSE_TOOLS,
    BD_GENERATE_TOOLS,
    fallback_retrieve,
    seo_keywords_artifact,
    _SOCIAL_PLATFORMS,
    _PRIMARY_CONTENT_TYPES,
)
from crews.react.runner import run_react_phase
from crews.react.bd_prompts import (
    BD_RETRIEVE_SYSTEM,
    BD_ANALYSE_SYSTEM,
    BD_GENERATE_SYSTEM,
)
from crews.bharat_desha.trend_agent import run_trend_agent
from crews.bharat_desha.seo_agent import run_seo_agent
from crews.bharat_desha.analysis_agent import run_analysis_agent
from crews.bharat_desha.content_agent import run_content_agent
from crews.bharat_desha.social_agent import run_social_agent


def _run_phase(runtime: ToolRuntime, tools, system_prompt: str, user_message: str) -> None:
    run_react_phase(tools, system_prompt, user_message)


def build_bharat_desha_graph():
    def _trend_node(state: CrewGraphState) -> dict:
        return {"trend_context": run_trend_agent(state["brief"].topic)}

    def _seo_node(state: CrewGraphState) -> dict:
        return {"seo_context": run_seo_agent(state["brief"].topic, state["trend_context"])}

    def _react_retrieve_node(state: CrewGraphState) -> dict:
        runtime = ToolRuntime(
            brief=state["brief"],
            db_path="",
            trend_context=state["trend_context"],
            seo_context=state["seo_context"],
        )
        token = set_runtime(runtime)
        try:
            user_message = (
                f"Travel research topic: {state['brief'].topic}\n"
                f"Primary SEO keyword: {state['seo_context'].get('primary_keyword', state['brief'].topic)}"
            )
            _run_phase(runtime, BD_RETRIEVE_TOOLS, BD_RETRIEVE_SYSTEM, user_message)
            if not runtime.retrieved:
                fallback_retrieve()
            return {"retrieved": runtime.retrieved}
        finally:
            reset_runtime(token)

    def _react_analyse_node(state: CrewGraphState) -> dict:
        runtime = ToolRuntime(
            brief=state["brief"],
            db_path="",
            retrieved=state["retrieved"],
            trend_context=state["trend_context"],
            seo_context=state["seo_context"],
        )
        token = set_runtime(runtime)
        try:
            user_message = (
                f"Analyse BharatDesha research for topic: {state['brief'].topic}. "
                f"Chunks available: {len(state['retrieved'])}"
            )
            _run_phase(runtime, BD_ANALYSE_TOOLS, BD_ANALYSE_SYSTEM, user_message)
            analysis = runtime.analysis
            if not is_valid_bd_analysis(analysis) and state["retrieved"]:
                if not any(k in analysis for k in ("spiritual", "key_points", "practical")):
                    analysis = run_analysis_agent(
                        state["retrieved"],
                        state["seo_context"],
                        state["trend_context"],
                    )
            return {"analysis": analysis}
        finally:
            reset_runtime(token)

    def _react_generate_node(state: CrewGraphState) -> dict:
        brief = state["brief"]
        seo_context = state["seo_context"]
        analysis = state["analysis"]
        primary_type = next(
            (a for a in brief.selected_artifacts if a in _PRIMARY_CONTENT_TYPES),
            None,
        )
        selected_platforms = [a for a in brief.selected_artifacts if a in _SOCIAL_PLATFORMS]

        runtime = ToolRuntime(
            brief=brief,
            db_path="",
            retrieved=state["retrieved"],
            analysis=analysis,
            trend_context=state["trend_context"],
            seo_context=seo_context,
            artifact_type=primary_type,
        )
        token = set_runtime(runtime)
        try:
            user_message = (
                f"Generate BharatDesha content for topic: {brief.topic}\n"
                f"Primary artifact type: {primary_type}\n"
                f"Social platforms: {selected_platforms}"
            )
            _run_phase(runtime, BD_GENERATE_TOOLS, BD_GENERATE_SYSTEM, user_message)

            artifacts = [seo_keywords_artifact(seo_context)]
            primary_artifact = runtime.primary_artifact
            if primary_type and not primary_artifact:
                primary_artifact = run_content_agent(
                    analysis,
                    seo_context,
                    artifact_type=primary_type,
                    tone=brief.tone,
                    depth=brief.depth,
                )
            if primary_artifact:
                artifacts.append(primary_artifact)

            social_in_runtime = [
                a for a in runtime.artifacts if a["type"] in _SOCIAL_PLATFORMS
            ]
            if social_in_runtime:
                artifacts.extend(social_in_runtime)
            elif selected_platforms and primary_artifact:
                artifacts.extend(
                    run_social_agent(
                        primary_artifact,
                        analysis.get("key_points", []),
                        seo_context,
                        platforms=selected_platforms,
                    )
                )

            return {"artifacts": artifacts}
        finally:
            reset_runtime(token)

    def _after_analysis(state: CrewGraphState) -> str:
        return analysis_route(state, is_valid_bd_analysis, max_retries=2)

    g = StateGraph(CrewGraphState)
    g.add_node("trend", _trend_node)
    g.add_node("seo", _seo_node)
    g.add_node("react_retrieve", _react_retrieve_node)
    g.add_node("react_analyse", _react_analyse_node)
    g.add_node("increment_retry", increment_retry_node)
    g.add_node("analysis_failed", analysis_failed_node)
    g.add_node("react_generate", _react_generate_node)

    g.add_edge(START, "trend")
    g.add_edge("trend", "seo")
    g.add_edge("seo", "react_retrieve")
    g.add_edge("react_retrieve", "react_analyse")
    g.add_conditional_edges("react_analyse", _after_analysis, {
        "continue": "react_generate",
        "retry": "increment_retry",
        "fail": "analysis_failed",
    })
    g.add_edge("increment_retry", "react_analyse")
    g.add_edge("analysis_failed", END)
    g.add_edge("react_generate", END)

    return g.compile()
