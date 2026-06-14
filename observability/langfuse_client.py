# observability/langfuse_client.py
import functools
from typing import Any, Dict, Optional, Tuple

import config

try:
    from langfuse.langchain import CallbackHandler
    _LANGFUSE_AVAILABLE = True
except ImportError:
    try:
        from langfuse.callback import CallbackHandler  # type: ignore[no-redef]
        _LANGFUSE_AVAILABLE = True
    except ImportError:
        CallbackHandler = None  # type: ignore[misc, assignment]
        _LANGFUSE_AVAILABLE = False

try:
    from langfuse import propagate_attributes as _propagate_attributes
except ImportError:
    _propagate_attributes = None


def is_langfuse_enabled() -> bool:
    return _LANGFUSE_AVAILABLE and bool(
        config.LANGFUSE_SECRET_KEY and config.LANGFUSE_PUBLIC_KEY
    )


def get_langfuse_handler(
    session_id: str,
    user_id: str = "anonymous",
    *,
    update_trace: bool = True,
):
    if not is_langfuse_enabled():
        return None
    return CallbackHandler(
        public_key=config.LANGFUSE_PUBLIC_KEY,
        update_trace=update_trace,
    )


def build_graph_invoke_config(
    *,
    session_id: Optional[str],
    user_id: str,
    run_name: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[Any], Dict[str, Any]]:
    if not is_langfuse_enabled():
        return None, {}
    handler = get_langfuse_handler(session_id or "anonymous", user_id)
    if handler is None:
        return None, {}
    invoke_config: Dict[str, Any] = {
        "callbacks": [handler],
        "run_name": run_name,
    }
    if metadata:
        invoke_config["metadata"] = metadata
    return handler, invoke_config


def extract_trace_id(handler: Any) -> Optional[str]:
    if handler is None:
        return None
    trace_id = getattr(handler, "last_trace_id", None)
    return str(trace_id) if trace_id else None


def flush_langfuse_handler(handler: Any) -> None:
    if handler is None:
        return
    client = getattr(handler, "client", None)
    if client is not None and hasattr(client, "flush"):
        client.flush()


def run_with_langfuse_context(
    fn,
    *,
    session_id: Optional[str] = None,
    user_id: str = "anonymous",
    metadata: Optional[Dict[str, str]] = None,
):
    if not is_langfuse_enabled() or _propagate_attributes is None:
        return fn()
    with _propagate_attributes(
        session_id=session_id,
        user_id=user_id,
        metadata=metadata,
    ):
        return fn()


def trace_agent_run(agent_name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator
