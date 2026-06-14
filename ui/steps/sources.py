import streamlit as st

from ui.components import phase_heading, source_card_html
from ui.session import advance_step


def render_step_sources() -> None:
    phase_heading(
        "Curate your sources",
        "Scored by recency, domain authority, and relevance. Select sources you trust.",
    )

    selected = []
    for src in st.session_state.sources:
        st.markdown(
            source_card_html(
                src["title"],
                src["domain"],
                src["date"],
                src["overall_score"],
            ),
            unsafe_allow_html=True,
        )
        if st.checkbox(
            f"Include · {src['title'][:80]}",
            key=f"src_{src['url']}",
        ):
            selected.append(src)

    if st.button("Confirm sources", type="primary") and selected:
        st.session_state.brief.selected_sources = selected
        advance_step(6)
