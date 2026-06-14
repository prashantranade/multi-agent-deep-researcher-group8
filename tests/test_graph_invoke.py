# tests/test_graph_invoke.py
from unittest.mock import MagicMock, patch

from crews.base_crew import ResearchBrief
from crews.graph_invoke import invoke_crew_graph, get_graph_run_config, set_graph_run_config, reset_graph_run_config
from crews.graph_state import make_initial_state


def _brief():
    return ResearchBrief(
        topic="Rajasthan travel",
        persona="content_creator",
        audience="millennials",
        tone="warm",
        depth="standard",
        selected_artifacts=["content_brief"],
    )


def test_invoke_crew_graph_without_langfuse():
    graph = MagicMock()
    graph.invoke.return_value = {"artifacts": [{"type": "content_brief", "content": "x", "citations": []}]}
    with patch("crews.graph_invoke.build_graph_invoke_config", return_value=(None, {})):
        result, trace_id = invoke_crew_graph(graph, make_initial_state(_brief()))
    graph.invoke.assert_called_once()
    assert graph.invoke.call_args.args[0]["brief"].topic == "Rajasthan travel"
    assert trace_id is None
    assert len(result["artifacts"]) == 1


def test_invoke_crew_graph_with_langfuse_callbacks():
    graph = MagicMock()
    graph.invoke.return_value = {"artifacts": []}
    mock_handler = MagicMock()
    mock_handler.last_trace_id = "trace-abc"
    invoke_config = {"callbacks": [mock_handler], "run_name": "content_creator_crew"}

    with patch("crews.graph_invoke.build_graph_invoke_config", return_value=(mock_handler, invoke_config)), \
         patch("crews.graph_invoke.run_with_langfuse_context", side_effect=lambda fn, **_: fn()), \
         patch("crews.graph_invoke.flush_langfuse_handler") as mock_flush:
        result, trace_id = invoke_crew_graph(
            graph,
            make_initial_state(_brief()),
            session_id="session-123",
        )

    graph.invoke.assert_called_once_with(
        graph.invoke.call_args.args[0],
        config=invoke_config,
    )
    mock_flush.assert_called_once_with(mock_handler)
    assert trace_id == "trace-abc"
    assert result == {"artifacts": []}


def test_get_graph_run_config_contextvar():
    token = set_graph_run_config({"callbacks": ["handler"], "run_name": "test"})
    try:
        assert get_graph_run_config() == {"callbacks": ["handler"], "run_name": "test"}
    finally:
        reset_graph_run_config(token)
    assert get_graph_run_config() is None
