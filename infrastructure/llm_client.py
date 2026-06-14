# infrastructure/llm_client.py
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import config

def get_llm(model: str) -> Any:
    """Returns a ChatOpenAI model with secondary Z.ai fallback."""
    primary = ChatOpenAI(
        model=model,
        openai_api_key=config.OPENROUTER_API_KEY or "dummy_key",
        openai_api_base="https://openrouter.ai/api/v1",
    )
    fallback = ChatOpenAI(
        model="glm-4-air",
        openai_api_key=config.ZAI_API_KEY or "dummy_key",
        openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
    )
    return primary.with_fallbacks([fallback])

def chat_with_fallback(messages: List[Dict[str, str]], model: str) -> str:
    llm = get_llm(model)
    lc_messages = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))
    response = llm.invoke(lc_messages)
    return str(response.content)

