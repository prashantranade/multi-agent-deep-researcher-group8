# tests/test_llm_client.py
import pytest
from unittest.mock import patch, MagicMock
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableWithFallbacks
from langchain_core.messages import AIMessage
from infrastructure.llm_client import get_llm, chat_with_fallback

def test_get_llm_returns_runnable_with_fallbacks():
    llm = get_llm("test-model")
    assert isinstance(llm, RunnableWithFallbacks)
    
    # Check primary
    assert isinstance(llm.runnable, ChatOpenAI)
    assert llm.runnable.model_name == "test-model"
    assert llm.runnable.openai_api_base == "https://openrouter.ai/api/v1"
    
    # Check fallback
    assert len(llm.fallbacks) == 1
    fallback = llm.fallbacks[0]
    assert isinstance(fallback, ChatOpenAI)
    assert fallback.model_name == "glm-4-air"
    assert fallback.openai_api_base == "https://open.bigmodel.cn/api/paas/v4/"

def test_chat_with_fallback_invokes_llm():
    mock_response = AIMessage(content="test response")
    with patch("infrastructure.llm_client.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = mock_response
        mock_get_llm.return_value = mock_llm
        
        result = chat_with_fallback(
            messages=[{"role": "user", "content": "hello"}],
            model="test-model"
        )
        
    assert result == "test response"
    mock_get_llm.assert_called_once_with("test-model")
    mock_llm.invoke.assert_called_once()

