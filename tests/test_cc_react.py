from unittest.mock import patch, MagicMock

from crews.react.runner import run_react_phase
from crews.tools.cc_tools import scrape_and_index_sources


def test_run_react_phase_invokes_create_react_agent():
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {"messages": []}
    with patch("crews.react.runner.create_react_agent", return_value=mock_agent) as mock_create, \
         patch("crews.react.runner.make_llm", return_value=MagicMock()), \
         patch("crews.react.runner.get_graph_run_config", return_value={"callbacks": ["cb"], "run_name": "phase"}):
        result = run_react_phase(
            [scrape_and_index_sources],
            "system prompt",
            "user message",
            model="openai/gpt-4o-mini",
        )
    mock_create.assert_called_once()
    mock_agent.invoke.assert_called_once()
    invoke_config = mock_agent.invoke.call_args.kwargs["config"]
    assert invoke_config["callbacks"] == ["cb"]
    assert invoke_config["run_name"] == "phase"
    assert invoke_config["recursion_limit"] == 12
    assert result == {"messages": []}
