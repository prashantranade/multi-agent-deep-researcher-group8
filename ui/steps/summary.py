import html

import streamlit as st

from ui.components import persona_label, phase_heading
from ui.constants import PHASES


def render_step_summary(step: int) -> None:
    label = dict(PHASES).get(step, f"Step {step}")
    phase_heading(f"Completed — {label}", "Read-only summary of this phase.")

    if step == 1:
        st.markdown(
            f'<div class="dr-summary">Lens: <strong>{html.escape(persona_label(st.session_state.get("persona")))}</strong></div>',
            unsafe_allow_html=True,
        )
    elif step == 2:
        st.markdown(
            f'<div class="dr-summary">Topic: <strong>{html.escape(st.session_state.get("topic", ""))}</strong></div>',
            unsafe_allow_html=True,
        )
    elif step == 3:
        has_ctx = bool(st.session_state.get("context_text"))
        st.markdown(
            f'<div class="dr-summary">Context: <strong>{"Added" if has_ctx else "Skipped"}</strong></div>',
            unsafe_allow_html=True,
        )
    elif step == 4:
        answers = st.session_state.get("answers") or {}
        lines = "<br>".join(
            f"{html.escape(k.title())}: {html.escape(v)}" for k, v in answers.items()
        )
        st.markdown(f'<div class="dr-summary">{lines}</div>', unsafe_allow_html=True)
    elif step == 5:
        brief = st.session_state.get("brief")
        count = len(brief.selected_sources) if brief else 0
        st.markdown(
            f'<div class="dr-summary">{count} source(s) selected.</div>',
            unsafe_allow_html=True,
        )
    elif step == 6:
        brief = st.session_state.get("brief")
        arts = ", ".join(brief.selected_artifacts) if brief else ""
        st.markdown(
            f'<div class="dr-summary">Outputs: {html.escape(arts)}</div>',
            unsafe_allow_html=True,
        )

    if st.button("Return to current step", key=f"back_from_summary_{step}"):
        st.session_state.view_step = None
        st.rerun()
