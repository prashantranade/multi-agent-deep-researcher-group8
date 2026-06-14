import streamlit as st

from ui.components import phase_heading
from ui.constants import ARTIFACT_OPTIONS
from ui.session import advance_step


def render_step_outputs() -> None:
    phase_heading("Choose deliverables", "Pick the artifact types your crew should generate.")

    persona = st.session_state.persona
    options = ARTIFACT_OPTIONS.get(persona, ARTIFACT_OPTIONS["content_creator"])

    if "selected_artifact_keys" not in st.session_state or not st.session_state.selected_artifact_keys:
        st.session_state.selected_artifact_keys = [options[0][0]]

    selected = set(st.session_state.selected_artifact_keys)

    cols = st.columns(min(len(options), 3))
    for i, (key, label) in enumerate(options):
        with cols[i % len(cols)]:
            is_on = key in selected
            btn_type = "primary" if is_on else "secondary"
            if st.button(label, key=f"artifact_{key}", type=btn_type, use_container_width=True):
                if is_on and len(selected) > 1:
                    selected.discard(key)
                elif not is_on:
                    selected.add(key)
                st.session_state.selected_artifact_keys = list(selected)
                st.rerun()

    if persona == "bharat_desha":
        st.caption("SEO keywords are always included in Bharat Desha runs.")

    if st.button("Run research crew", type="primary") and selected:
        st.session_state.brief.selected_artifacts = list(selected)
        advance_step(7)
