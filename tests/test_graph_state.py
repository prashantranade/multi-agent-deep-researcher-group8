from crews.graph_state import CrewGraphState, make_initial_state
from crews.base_crew import ResearchBrief
from crews.graph_utils import is_valid_cc_analysis, is_valid_pm_analysis, analysis_route


def test_make_initial_state_has_required_keys():
    brief = ResearchBrief(
        topic="test", persona="content_creator",
        audience="general", tone="neutral", depth="standard",
    )
    state = make_initial_state(brief)
    assert state["brief"] is brief
    assert state["retrieved"] == []
    assert state["analysis"] == {}
    assert state["artifacts"] == []
    assert state["retry_count"] == 0


def test_is_valid_cc_analysis_requires_trends_or_hooks():
    assert is_valid_cc_analysis({"trends": ["x"], "hooks": []}) is True
    assert is_valid_cc_analysis({"trends": [], "hooks": []}) is False


def test_analysis_route_retries_then_fails():
    state: CrewGraphState = {
        "brief": ResearchBrief(
            topic="t", persona="content_creator", audience="a", tone="t", depth="standard",
        ),
        "retrieved": [],
        "analysis": {},
        "artifacts": [],
        "errors": [],
        "retry_count": 0,
        "trend_context": None,
        "seo_context": None,
    }
    assert analysis_route(state, is_valid_cc_analysis, max_retries=2) == "retry"
    state["retry_count"] = 2
    assert analysis_route(state, is_valid_cc_analysis, max_retries=2) == "fail"
    state["analysis"] = {"trends": ["eco"]}
    assert analysis_route(state, is_valid_cc_analysis, max_retries=2) == "continue"


def test_is_valid_pm_analysis():
    assert is_valid_pm_analysis({"market_size": "large", "competitors": []}) is True
    assert is_valid_pm_analysis({"market_size": "unknown", "competitors": []}) is False
