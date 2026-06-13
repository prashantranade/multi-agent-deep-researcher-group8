# tests/test_langfuse_client.py
from unittest.mock import patch, MagicMock
import sys

def test_get_langfuse_handler_returns_handler():
    mock_cb_class = MagicMock()
    mock_handler = MagicMock()
    mock_cb_class.return_value = mock_handler

    with patch.dict("sys.modules", {"langfuse.callback": MagicMock(CallbackHandler=mock_cb_class)}):
        # Re-import to pick up the mock
        if "observability.langfuse_client" in sys.modules:
            del sys.modules["observability.langfuse_client"]
        import importlib
        import observability.langfuse_client as lf_module
        importlib.reload(lf_module)

        handler = lf_module.get_langfuse_handler(session_id="test-123", user_id="user-1")
        assert handler is not None
        mock_cb_class.assert_called_once()

def test_trace_agent_run_wraps_function():
    from observability.langfuse_client import trace_agent_run
    called = {}
    def my_fn(*args, **kwargs):
        called["yes"] = True
        return "result"
    wrapped = trace_agent_run("test-agent")(my_fn)
    result = wrapped()
    assert called.get("yes") is True
    assert result == "result"
