# tests/test_langfuse_client.py
from unittest.mock import patch, MagicMock
import sys


def test_is_langfuse_enabled_requires_keys():
    from observability import langfuse_client
    with patch.object(langfuse_client, "_LANGFUSE_AVAILABLE", True):
        with patch.object(langfuse_client.config, "LANGFUSE_SECRET_KEY", "secret"), \
             patch.object(langfuse_client.config, "LANGFUSE_PUBLIC_KEY", "public"):
            assert langfuse_client.is_langfuse_enabled() is True
        with patch.object(langfuse_client.config, "LANGFUSE_SECRET_KEY", None):
            assert langfuse_client.is_langfuse_enabled() is False


def test_get_langfuse_handler_returns_handler():
    mock_cb_class = MagicMock()
    mock_handler = MagicMock()
    mock_cb_class.return_value = mock_handler

    with patch.dict("sys.modules", {"langfuse.langchain": MagicMock(CallbackHandler=mock_cb_class)}):
        if "observability.langfuse_client" in sys.modules:
            del sys.modules["observability.langfuse_client"]
        import importlib
        import observability.langfuse_client as lf_module
        importlib.reload(lf_module)

        with patch.object(lf_module, "is_langfuse_enabled", return_value=True):
            handler = lf_module.get_langfuse_handler(session_id="test-123", user_id="user-1")
        assert handler is not None
        mock_cb_class.assert_called_once()


def test_build_graph_invoke_config_returns_callbacks():
    from observability.langfuse_client import build_graph_invoke_config

    mock_handler = MagicMock()
    with patch("observability.langfuse_client.is_langfuse_enabled", return_value=True), \
         patch("observability.langfuse_client.get_langfuse_handler", return_value=mock_handler):
        handler, config = build_graph_invoke_config(
            session_id="sess-1",
            user_id="user-1",
            run_name="content_creator_crew",
            metadata={"topic": "travel"},
        )
    assert handler is mock_handler
    assert config["callbacks"] == [mock_handler]
    assert config["run_name"] == "content_creator_crew"
    assert config["metadata"]["topic"] == "travel"


def test_extract_trace_id_from_handler():
    from observability.langfuse_client import extract_trace_id

    handler = MagicMock(last_trace_id="abc-123")
    assert extract_trace_id(handler) == "abc-123"
    assert extract_trace_id(None) is None


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
