import streamlit as st

from ui.components import persona_card_html, phase_heading
from ui.constants import PERSONAS
from ui.session import advance_step


def render_step_persona() -> None:
    phase_heading("Choose your lens", "Each crew researches and writes with a different focus.")

    cols = st.columns(len(PERSONAS))
    for col, persona in zip(cols, PERSONAS):
        with col:
            selected = st.session_state.get("persona") == persona["key"]
            st.markdown(
                persona_card_html(persona["title"], persona["promise"], selected),
                unsafe_allow_html=True,
            )
            if st.button("Select", key=f"persona_{persona['key']}", use_container_width=True):
                st.session_state.persona = persona["key"]
                st.rerun()

    if st.button(
        "Continue to topic",
        type="primary",
        disabled=not st.session_state.get("persona"),
    ):
        advance_step(2)
