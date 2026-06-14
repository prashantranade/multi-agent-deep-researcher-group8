import streamlit as st

from ui.components import dossier_field, persona_label


def _status(step: int) -> str:
    if step >= 7:
        return "Complete"
    if step == 6:
        return "Ready to run"
    if step >= 5:
        return "Curating sources"
    if step >= 4:
        return "Building brief"
    if step >= 2:
        return "In progress"
    return "Starting"


def render_dossier() -> None:
    step = st.session_state.step
    answers = st.session_state.get("answers") or {}
    persona = st.session_state.get("persona")
    topic = st.session_state.get("topic", "")
    brief = st.session_state.get("brief")

    context_note = "✓ Added" if st.session_state.get("context_text") else "—"
    sources_count = ""
    if brief and getattr(brief, "selected_sources", None):
        sources_count = str(len(brief.selected_sources))
    elif st.session_state.get("sources"):
        sources_count = f"{len(st.session_state.sources)} found"

    outputs = ""
    if brief and getattr(brief, "selected_artifacts", None):
        outputs = ", ".join(a.replace("_", " ") for a in brief.selected_artifacts)
    elif st.session_state.get("selected_artifact_keys"):
        outputs = ", ".join(
            k.replace("_", " ") for k in st.session_state.selected_artifact_keys
        )

    fields = [
        dossier_field("Lens", persona_label(persona), empty=not persona),
        dossier_field("Topic", topic, empty=not topic),
        dossier_field("Audience", answers.get("audience", ""), empty="audience" not in answers),
        dossier_field("Tone", answers.get("tone", ""), empty="tone" not in answers),
        dossier_field("Depth", answers.get("depth", ""), empty="depth" not in answers),
        dossier_field("Context", context_note, mono=True),
        dossier_field("Sources", sources_count, mono=True, empty=not sources_count),
        dossier_field("Outputs", outputs, mono=True, empty=not outputs),
        dossier_field("Status", _status(step), mono=True),
    ]

    if persona == "bharat_desha":
        fields.insert(
            -1,
            dossier_field(
                "Note",
                "SEO keywords included automatically",
                mono=True,
            ),
        )

    body = "".join(fields)
    st.markdown(
        f"""
        <div class="dr-dossier">
            <div class="dr-dossier__title">Research file</div>
            {body}
        </div>
        """,
        unsafe_allow_html=True,
    )
