# tests/test_langfuse_client.py
from unittest.mock import patch, MagicMock
from observability.langfuse_client import get_langfuse_handler, trace_agent_run
import config

def test_get_langfuse_handler_returns_handler():
    with patch("observability.langfuse_client.CallbackHandler") as mock_cb:
        mock_cb.return_value = MagicMock()
        handler = get_langfuse_handler(session_id="test-123", user_id="user-1")
        assert handler is not None
        mock_cb.assert_called_once_with(
            secret_key=config.LANGFUSE_SECRET_KEY,
            public_key=config.LANGFUSE_PUBLIC_KEY,
            host=config.LANGFUSE_HOST,
            session_id="test-123",
            user_id="user-1",
        )

def test_trace_agent_run_wraps_function():
    called = {}
    def my_fn(*args, **kwargs):
        called["yes"] = True
        return "result"
    wrapped = trace_agent_run("test-agent")(my_fn)
    result = wrapped()
    assert called.get("yes") is True
    assert result == "result"
