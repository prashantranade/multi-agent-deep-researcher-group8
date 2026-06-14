from typing import Callable, Dict, Any

from crews.graph_state import CrewGraphState


def is_valid_cc_analysis(analysis: Dict[str, Any]) -> bool:
    return bool(analysis.get("trends") or analysis.get("hooks"))


def is_valid_pm_analysis(analysis: Dict[str, Any]) -> bool:
    market = analysis.get("market_size", "unknown")
    return market != "unknown" or bool(analysis.get("competitors"))


def is_valid_bd_analysis(analysis: Dict[str, Any]) -> bool:
    return bool(analysis.get("spiritual") or analysis.get("key_points"))


def analysis_route(
    state: CrewGraphState,
    validator: Callable[[Dict[str, Any]], bool],
    max_retries: int = 2,
) -> str:
    if validator(state["analysis"]):
        return "continue"
    if state.get("retry_count", 0) < max_retries:
        return "retry"
    return "fail"


def increment_retry_node(state: CrewGraphState) -> dict:
    return {"retry_count": state.get("retry_count", 0) + 1}


def analysis_failed_node(state: CrewGraphState) -> dict:
    return {"errors": ["Analysis failed after retries: invalid or empty JSON response"]}
