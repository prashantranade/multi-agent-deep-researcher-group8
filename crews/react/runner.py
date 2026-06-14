from typing import Any, Mapping, Sequence

from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent

import config
from infrastructure.llm_factory import make_llm
from crews.graph_invoke import get_graph_run_config


def run_react_phase(
    tools: Sequence[BaseTool],
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    recursion_limit: int = 12,
    run_config: Mapping[str, Any] | None = None,
) -> dict:
    llm = make_llm(model or config.ANALYSIS_MODEL)
    agent = create_react_agent(llm, list(tools), prompt=system_prompt)
    invoke_config: dict[str, Any] = {"recursion_limit": recursion_limit}
    parent_config = run_config or get_graph_run_config()
    if parent_config:
        invoke_config = {**parent_config, **invoke_config}
    return agent.invoke(
        {"messages": [HumanMessage(content=user_message)]},
        config=invoke_config,
    )
