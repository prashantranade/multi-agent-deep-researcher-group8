import uuid

import streamlit as st


def init_session_state() -> None:
    defaults = {
        "session_id": str(uuid.uuid4()),
        "step": 1,
        "answers": {},
        "context_text": "",
        "brief": None,
        "sources": [],
        "view_step": None,
        "selected_artifact_keys": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_view_on_forward() -> None:
    view = st.session_state.get("view_step")
    if view is not None and view >= st.session_state.step:
        st.session_state.view_step = None


def advance_step(next_step: int) -> None:
    st.session_state.view_step = None
    st.session_state.step = next_step
    st.rerun()
