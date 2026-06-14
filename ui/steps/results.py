import html

import streamlit as st

from crews.router import get_crew
from infrastructure.artifact_exporter import export_artifact
from ui.agent_theater import render_pipeline
from ui.components import phase_heading


def render_step_results() -> None:
    phase_heading("Deliverables", "Your agent crew is producing source-verified artifacts.")

    persona = st.session_state.persona
    complete = "artifacts" in st.session_state

    render_pipeline(persona, running=not complete, complete=complete)

    if not complete:
        with st.spinner("Agent crew working…"):
            try:
                crew = get_crew(persona)
                result = crew.run(
                    st.session_state.brief,
                    session_id=st.session_state.session_id,
                )
                st.session_state.artifacts = result.artifacts
                if result.trace_id:
                    st.session_state.trace_id = result.trace_id
                st.rerun()
            except Exception as e:
                st.error(f"Research crew failed: {e}")
                st.stop()

    render_pipeline(persona, complete=True)

    for artifact in st.session_state.get("artifacts", []):
        title = artifact["type"].replace("_", " ").title()
        exported = export_artifact(artifact)
        st.markdown(
            f"""
            <div class="dr-artifact">
                <div class="dr-artifact__title">{html.escape(title)}</div>
                <div class="dr-artifact-body"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(exported)
        st.download_button(
            f"Download {artifact['type']}",
            exported,
            file_name=f"{artifact['type']}.md",
            key=f"dl_{artifact['type']}",
        )

    if st.session_state.get("trace_id"):
        st.caption(f"LangFuse trace: `{st.session_state.trace_id}`")

    if st.button("Start new research", key="restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
