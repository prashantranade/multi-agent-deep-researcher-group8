from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from crews.graph_state import CrewGraphState
from crews.graph_utils import (
    analysis_route,
    increment_retry_node,
    analysis_failed_node,
    is_valid_cc_analysis,
)
from crews.tools.tool_context import ToolRuntime, set_runtime, reset_runtime
from crews.tools.cc_tools import (
    CC_RETRIEVE_TOOLS,
    CC_ANALYSE_TOOLS,
    CC_GENERATE_TOOLS,
    fallback_retrieve,
)
from crews.react.runner import run_react_phase
from crews.react.cc_prompts import (
    CC_RETRIEVE_SYSTEM,
    CC_ANALYSE_SYSTEM,
    CC_GENERATE_SYSTEM,
)
from crews.content_creator.analysis_agent import CCAnalysisAgent


def _run_phase(runtime: ToolRuntime, tools, system_prompt: str, user_message: str) -> None:
    run_react_phase(tools, system_prompt, user_message)


def build_content_creator_graph(db_path: str = ".lancedb_cc"):
    def _react_retrieve_node(state: CrewGraphState) -> dict:
        runtime = ToolRuntime(brief=state["brief"], db_path=db_path)
        token = set_runtime(runtime)
        try:
            user_message = (
                f"Research topic: {state['brief'].topic}\n"
                f"Audience: {state['brief'].audience}\n"
                f"Selected sources: {len(state['brief'].selected_sources)}"
            )
            _run_phase(runtime, CC_RETRIEVE_TOOLS, CC_RETRIEVE_SYSTEM, user_message)
            if not runtime.retrieved:
                fallback_retrieve(db_path)
            return {"retrieved": runtime.retrieved}
        finally:
            reset_runtime(token)

    def _react_analyse_node(state: CrewGraphState) -> dict:
        runtime = ToolRuntime(
            brief=state["brief"],
            db_path=db_path,
            retrieved=state["retrieved"],
        )
        token = set_runtime(runtime)
        try:
            user_message = (
                f"Analyse research for topic: {state['brief'].topic}. "
                f"Chunks available: {len(state['retrieved'])}"
            )
            _run_phase(runtime, CC_ANALYSE_TOOLS, CC_ANALYSE_SYSTEM, user_message)
            analysis = runtime.analysis
            if not analysis and state["retrieved"]:
                analysis = CCAnalysisAgent().analyse(state["retrieved"])
            return {"analysis": analysis}
        finally:
            reset_runtime(token)

    def _react_generate_node(state: CrewGraphState) -> dict:
        runtime = ToolRuntime(
            brief=state["brief"],
            db_path=db_path,
            retrieved=state["retrieved"],
            analysis=state["analysis"],
            artifact_type=state.get("artifact_type"),
        )
        token = set_runtime(runtime)
        try:
            artifact_type = state["artifact_type"]
            user_message = (
                f"Generate artifact type '{artifact_type}' for topic: {state['brief'].topic}"
            )
            _run_phase(runtime, CC_GENERATE_TOOLS, CC_GENERATE_SYSTEM, user_message)
            if runtime.artifacts:
                return {"artifacts": runtime.artifacts}
            from crews.content_creator.output_agent import CCOutputAgent

            artifacts = CCOutputAgent().generate_artifacts(state["analysis"], [artifact_type])
            return {"artifacts": artifacts}
        finally:
            reset_runtime(token)

    def _after_analysis(state: CrewGraphState):
        route = analysis_route(state, is_valid_cc_analysis, max_retries=2)
        if route == "continue":
            return [
                Send("react_generate", {**state, "artifact_type": t})
                for t in state["brief"].selected_artifacts
            ]
        return route

    g = StateGraph(CrewGraphState)
    g.add_node("react_retrieve", _react_retrieve_node)
    g.add_node("react_analyse", _react_analyse_node)
    g.add_node("increment_retry", increment_retry_node)
    g.add_node("analysis_failed", analysis_failed_node)
    g.add_node("react_generate", _react_generate_node)

    g.add_edge(START, "react_retrieve")
    g.add_edge("react_retrieve", "react_analyse")
    g.add_conditional_edges("react_analyse", _after_analysis, {
        "retry": "increment_retry",
        "fail": "analysis_failed",
    })
    g.add_edge("increment_retry", "react_analyse")
    g.add_edge("analysis_failed", END)
    g.add_edge("react_generate", END)

    return g.compile()
