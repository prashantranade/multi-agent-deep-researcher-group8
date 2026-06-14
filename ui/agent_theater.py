import html

import streamlit as st

from ui.constants import PIPELINES


def render_pipeline(persona: str, *, running: bool = False, complete: bool = False) -> None:
    nodes = PIPELINES.get(persona, PIPELINES["content_creator"])
    parts = []
    for i, name in enumerate(nodes):
        if complete:
            cls = "dr-pipeline__node dr-pipeline__node--done"
        elif running and i == 0:
            cls = "dr-pipeline__node dr-pipeline__node--active"
        elif running:
            cls = "dr-pipeline__node"
        else:
            cls = "dr-pipeline__node"
        parts.append(f'<span class="{cls}">{html.escape(name)}</span>')
        if i < len(nodes) - 1:
            parts.append('<span class="dr-pipeline__arrow">→</span>')

    st.markdown(
        f'<div class="dr-pipeline">{"".join(parts)}</div>',
        unsafe_allow_html=True,
    )

    if running:
        st.caption("Running research crew — retrieve, analyse, and generate (30–60 seconds).")
    elif complete:
        st.caption("Crew run complete.")
