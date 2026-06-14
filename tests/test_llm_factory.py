from unittest.mock import patch, MagicMock

from infrastructure.llm_factory import make_llm


def test_make_llm_creates_openrouter_client():
    with patch("infrastructure.llm_factory.ChatOpenAI") as mock_chat:
        primary = MagicMock()
        mock_chat.return_value = primary
        with patch("infrastructure.llm_factory.config.ZAI_API_KEY", None):
            result = make_llm("openai/gpt-4o-mini")
    assert result is primary
    mock_chat.assert_called_once()
    call_kwargs = mock_chat.call_args.kwargs
    assert call_kwargs["base_url"] == "https://openrouter.ai/api/v1"


def test_make_llm_adds_fallback_when_zai_key_present():
    with patch("infrastructure.llm_factory.ChatOpenAI") as mock_chat:
        primary = MagicMock()
        fallback = MagicMock()
        primary.with_fallbacks.return_value = "llm-with-fallback"
        mock_chat.side_effect = [primary, fallback]
        with patch("infrastructure.llm_factory.config.ZAI_API_KEY", "zai-key"):
            result = make_llm("anthropic/claude-sonnet-4-5")
    assert result == "llm-with-fallback"
    primary.with_fallbacks.assert_called_once_with([fallback])
