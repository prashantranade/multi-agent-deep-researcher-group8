import streamlit as st

from ui.components import phase_heading
from ui.session import advance_step


def render_step_topic() -> None:
    phase_heading(
        "What do you want to research?",
        "Name the topic your agent crew will investigate.",
    )
    topic = st.text_input(
        "Research topic",
        value=st.session_state.get("topic", ""),
        placeholder="e.g. Sustainable travel in Rajasthan for millennials",
        label_visibility="collapsed",
    )
    if st.button("Continue to context", type="primary") and topic.strip():
        st.session_state.topic = topic.strip()
        advance_step(3)
