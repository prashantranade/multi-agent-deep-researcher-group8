from contextvars import ContextVar, Token
from typing import Any, Dict, Optional, Tuple

from crews.graph_state import CrewGraphState
from observability.langfuse_client import (
    build_graph_invoke_config,
    extract_trace_id,
    flush_langfuse_handler,
    run_with_langfuse_context,
)

_graph_run_config: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "graph_run_config", default=None
)


def set_graph_run_config(config: Optional[Dict[str, Any]]) -> Token:
    return _graph_run_config.set(config)


def reset_graph_run_config(token: Token) -> None:
    _graph_run_config.reset(token)


def get_graph_run_config() -> Optional[Dict[str, Any]]:
    return _graph_run_config.get()


def invoke_crew_graph(
    graph,
    state: CrewGraphState,
    *,
    session_id: Optional[str] = None,
    user_id: str = "anonymous",
) -> Tuple[dict, Optional[str]]:
    brief = state["brief"]
    run_name = f"{brief.persona}_crew"
    metadata = {
        "topic": brief.topic,
        "persona": brief.persona,
        "depth": brief.depth,
        "audience": brief.audience,
    }
    handler, invoke_config = build_graph_invoke_config(
        session_id=session_id,
        user_id=user_id,
        run_name=run_name,
        metadata=metadata,
    )

    token = set_graph_run_config(invoke_config or None)
    try:

        def _invoke() -> dict:
            if invoke_config:
                return graph.invoke(state, config=invoke_config)
            return graph.invoke(state)

        result = run_with_langfuse_context(
            _invoke,
            session_id=session_id,
            user_id=user_id,
            metadata={k: str(v) for k, v in metadata.items()},
        )
        flush_langfuse_handler(handler)
        return result, extract_trace_id(handler)
    finally:
        reset_graph_run_config(token)
