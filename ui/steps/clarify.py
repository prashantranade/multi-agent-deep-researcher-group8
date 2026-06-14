import streamlit as st

from intake.clarification_agent import ClarificationAgent
from source_engine.confidence_scorer import score_sources
from source_engine.discovery import discover_sources
from ui.components import phase_heading
from ui.constants import CLARIFY_FIELDS
from ui.session import advance_step


def render_step_clarify() -> None:
    phase_heading("Sharpen your brief", "A few questions so the crew knows your audience and depth.")

    agent = ClarificationAgent()
    answers = st.session_state.answers
    answered = len(answers)
    total = len(CLARIFY_FIELDS)
    st.caption(f"Question {min(answered + 1, total)} of {total}")

    next_q = agent.get_next_question(
        st.session_state.topic,
        st.session_state.persona,
        st.session_state.context_text,
        answers,
    )

    if next_q:
        field, question = next_q
        answer = st.text_input(question, key=f"clarify_{field}")
        if st.button("Next", type="primary") and answer.strip():
            st.session_state.answers[field] = answer.strip()
            st.rerun()
    else:
        st.success("Brief complete. Ready to discover sources.")
        if st.button("Discover sources", type="primary", key="discover_sources"):
            brief = agent.build_brief(
                st.session_state.topic,
                st.session_state.persona,
                st.session_state.context_text,
                st.session_state.answers,
            )
            st.session_state.brief = brief
            with st.spinner("Discovering sources…"):
                raw = discover_sources(st.session_state.topic)
                st.session_state.sources = score_sources(raw)
            advance_step(5)
