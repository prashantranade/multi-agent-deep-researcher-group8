from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from crews.base_crew import ResearchBrief


@dataclass
class ToolRuntime:
    brief: ResearchBrief
    db_path: str
    retrieved: List[Dict[str, Any]] = field(default_factory=list)
    analysis: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    artifact_type: Optional[str] = None
    trend_context: Optional[Dict[str, Any]] = None
    seo_context: Optional[Dict[str, Any]] = None
    primary_artifact: Optional[Dict[str, Any]] = None


_runtime: ContextVar[Optional[ToolRuntime]] = ContextVar("tool_runtime", default=None)


def set_runtime(runtime: ToolRuntime) -> Token:
    return _runtime.set(runtime)


def reset_runtime(token: Token) -> None:
    _runtime.reset(token)


def get_runtime() -> ToolRuntime:
    runtime = _runtime.get()
    if runtime is None:
        raise RuntimeError("Tool runtime is not set for this crew execution")
    return runtime
