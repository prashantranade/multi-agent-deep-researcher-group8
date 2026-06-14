import streamlit as st

from intake.context_enrichment import (
    build_context_text,
    enrich_from_file,
    enrich_from_handle,
    enrich_from_url,
)
from ui.components import phase_heading
from ui.session import advance_step


def _save_context(url_input: str, handle_input: str, uploaded_files) -> None:
    url_text = enrich_from_url(url_input) if url_input else ""
    handle_text = enrich_from_handle(handle_input) if handle_input else ""
    file_texts = []
    for f in uploaded_files or []:
        file_texts.append(enrich_from_file(f.read(), f.name, f.type))
    file_text = "\n\n".join(file_texts)
    st.session_state.context_text = build_context_text(url_text, file_text, handle_text)


def render_step_context() -> None:
    phase_heading(
        "Bring your materials",
        "Optional — URL, social handle, or documents to enrich your brief.",
    )
    url_input = st.text_input(
        "Your website or relevant URL",
        placeholder="https://bharatdesha.com",
    )
    handle_input = st.text_input(
        "Social media handle",
        placeholder="@bharatdesha",
    )
    uploaded_files = st.file_uploader(
        "Upload documents or images",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Continue to clarify", type="primary"):
            _save_context(url_input, handle_input, uploaded_files)
            advance_step(4)
    with col2:
        if st.button("Skip for now"):
            st.session_state.context_text = st.session_state.get("context_text") or ""
            advance_step(4)
