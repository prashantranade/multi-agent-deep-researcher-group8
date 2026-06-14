# app.py
import streamlit as st

from ui.dossier import render_dossier
from ui.session import init_session_state
from ui.spine import render_spine
from ui.theme import inject_theme
from ui.components import render_header
from ui.steps.persona import render_step_persona
from ui.steps.topic import render_step_topic
from ui.steps.context import render_step_context
from ui.steps.clarify import render_step_clarify
from ui.steps.sources import render_step_sources
from ui.steps.outputs import render_step_outputs
from ui.steps.results import render_step_results
from ui.steps.summary import render_step_summary


STEP_RENDERERS = {
    1: render_step_persona,
    2: render_step_topic,
    3: render_step_context,
    4: render_step_clarify,
    5: render_step_sources,
    6: render_step_outputs,
}


def main() -> None:
    st.set_page_config(page_title="Deep Researcher", layout="wide", page_icon="📚")
    init_session_state()
    inject_theme()
    render_header()

    if st.session_state.step == 7:
        render_step_results()
        return

    col_spine, col_dossier, col_work = st.columns([1, 1.4, 3.6])

    with col_spine:
        active_step = render_spine(st.session_state.step)

    with col_dossier:
        st.markdown('<div class="dr-dossier-col">', unsafe_allow_html=True)
        render_dossier()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_work:
        st.markdown('<div class="dr-workspace">', unsafe_allow_html=True)
        view = st.session_state.get("view_step")
        if view and view < st.session_state.step:
            render_step_summary(view)
        else:
            renderer = STEP_RENDERERS.get(active_step)
            if renderer:
                renderer()
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
