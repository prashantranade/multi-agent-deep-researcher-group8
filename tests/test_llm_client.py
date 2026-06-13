# tests/test_llm_client.py
import pytest
from unittest.mock import patch, MagicMock
import openai
from infrastructure.llm_client import chat_with_fallback, _call_provider, _PROVIDERS

def test_primary_succeeds_no_fallback():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "primary response"
    with patch("infrastructure.llm_client._call_provider") as mock_call:
        mock_call.return_value = mock_response
        result = chat_with_fallback(
            messages=[{"role": "user", "content": "hello"}],
            model="claude-sonnet-4-6"
        )
    assert result == "primary response"
    assert mock_call.call_count == 1

def test_primary_rate_limit_triggers_fallback():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "fallback response"
    with patch("infrastructure.llm_client._call_provider") as mock_call:
        mock_call.side_effect = [
            openai.RateLimitError("rate limit", response=MagicMock(), body={}),
            mock_response,
        ]
        result = chat_with_fallback(
            messages=[{"role": "user", "content": "hello"}],
            model="claude-sonnet-4-6"
        )
    assert result == "fallback response"
    assert mock_call.call_count == 2

def test_api_status_error_triggers_fallback():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "fallback response"
    with patch("infrastructure.llm_client._call_provider") as mock_call:
        mock_call.side_effect = [
            openai.APIStatusError("server error", response=MagicMock(), body={}),
            mock_response,
        ]
        result = chat_with_fallback(
            messages=[{"role": "user", "content": "hello"}],
            model="claude-sonnet-4-6"
        )
    assert result == "fallback response"
    assert mock_call.call_count == 2

def test_both_providers_fail_raises_runtime_error():
    with patch("infrastructure.llm_client._call_provider") as mock_call:
        mock_call.side_effect = openai.RateLimitError(
            "rate limit", response=MagicMock(), body={}
        )
        with pytest.raises(RuntimeError, match="All LLM providers exhausted"):
            chat_with_fallback(
                messages=[{"role": "user", "content": "hello"}],
                model="claude-sonnet-4-6"
            )

def test_providers_config():
    assert len(_PROVIDERS) == 2
    assert _PROVIDERS[0]["name"] == "openrouter"
    assert _PROVIDERS[1]["name"] == "zai"
    assert _PROVIDERS[1]["model_override"] == "glm-4-air"
