# infrastructure/llm_client.py
from typing import List, Dict, Any
import openai
import config

_PROVIDERS = [
    {
        "name": "openrouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_attr": "OPENROUTER_API_KEY",
        "model_override": None,          # use the model requested as-is
    },
    {
        "name": "zai",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "api_key_attr": "ZAI_API_KEY",
        "model_override": "glm-4-air",  # Z.ai free fallback model
    },
]

def _call_provider(provider: Dict, messages: List[Dict], model: str) -> Any:
    client = openai.OpenAI(
        api_key=getattr(config, provider["api_key_attr"]),
        base_url=provider["base_url"],
    )
    effective_model = provider["model_override"] or model
    return client.chat.completions.create(
        model=effective_model,
        messages=messages,
    )

def chat_with_fallback(messages: List[Dict[str, str]], model: str) -> str:
    last_error = None
    for provider in _PROVIDERS:
        try:
            response = _call_provider(provider, messages, model)
            return response.choices[0].message.content
        except (openai.RateLimitError, openai.APIStatusError, openai.APIConnectionError) as e:
            last_error = e
            continue
    raise RuntimeError(f"All LLM providers exhausted. Last error: {last_error}")
