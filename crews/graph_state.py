from typing import TypedDict, List, Dict, Any, Optional, Annotated, NotRequired
import operator

from crews.base_crew import ResearchBrief


class CrewGraphState(TypedDict):
    brief: ResearchBrief
    retrieved: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    artifacts: Annotated[List[Dict[str, Any]], operator.add]
    errors: Annotated[List[str], operator.add]
    retry_count: int
    trend_context: Optional[Dict[str, Any]]
    seo_context: Optional[Dict[str, Any]]
    artifact_type: NotRequired[Optional[str]]


def make_initial_state(brief: ResearchBrief) -> CrewGraphState:
    return CrewGraphState(
        brief=brief,
        retrieved=[],
        analysis={},
        artifacts=[],
        errors=[],
        retry_count=0,
        trend_context=None,
        seo_context=None,
    )
