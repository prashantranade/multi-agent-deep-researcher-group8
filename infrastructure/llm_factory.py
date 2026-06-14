from langchain_openai import ChatOpenAI

import config


def make_llm(model: str, temperature: float = 0.3) -> ChatOpenAI:
    """LangChain chat model with OpenRouter primary and optional Z.ai fallback."""
    primary = ChatOpenAI(
        model=model,
        api_key=config.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
    )
    if config.ZAI_API_KEY:
        fallback = ChatOpenAI(
            model="glm-4-air",
            api_key=config.ZAI_API_KEY,
            base_url="https://open.bigmodel.cn/api/paas/v4/",
            temperature=temperature,
        )
        return primary.with_fallbacks([fallback])
    return primary
