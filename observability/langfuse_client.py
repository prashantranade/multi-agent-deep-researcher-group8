# observability/langfuse_client.py
import functools
from langfuse.callback import CallbackHandler
import config

def get_langfuse_handler(session_id: str, user_id: str = "anonymous") -> CallbackHandler:
    return CallbackHandler(
        secret_key=config.LANGFUSE_SECRET_KEY,
        public_key=config.LANGFUSE_PUBLIC_KEY,
        host=config.LANGFUSE_HOST,
        session_id=session_id,
        user_id=user_id,
    )

def trace_agent_run(agent_name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # TODO: attach LangFuse span when session_id is available in context
            return fn(*args, **kwargs)
        return wrapper
    return decorator
