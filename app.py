# app.py — minimal stub if Squad 1 hasn't merged yet
import streamlit as st
from uuid import uuid4
from crews.router import get_crew
from ui.artifact_renderer import render_artifact
from observability.langfuse_client import get_langfuse_handler
from intake.persona_selector import PERSONAS
from crews.base_crew import ResearchBrief

st.set_page_config(page_title="Multi-Agent Deep Researcher", layout="wide")
st.title("Multi-Agent Deep Researcher")

# Persona selection
persona = st.selectbox(
    "Select your persona",
    options=list(PERSONAS.keys()),
    format_func=lambda k: PERSONAS[k]["label"],
)

topic = st.text_input("Research topic")
audience = st.text_input("Target audience", value="general audience")
tone = st.selectbox("Tone", ["informative", "warm", "analytical", "professional"])
depth = st.selectbox("Depth", ["quick", "standard", "deep"])

available_artifacts = PERSONAS[persona]["artifacts"]
selected_artifacts = st.multiselect(
    "Select artifacts to generate",
    options=available_artifacts,
    default=available_artifacts[:2],
)

# Always include persona's mandatory artifacts
always_included = PERSONAS[persona].get("always_included", [])
final_artifacts = list(set(selected_artifacts + always_included))

if st.button("Run Research") and topic:
    session_id = str(uuid4())
    langfuse_handler = get_langfuse_handler(session_id=session_id, user_id="demo")

    brief = ResearchBrief(
        topic=topic,
        persona=persona,
        audience=audience,
        tone=tone,
        depth=depth,
        selected_artifacts=final_artifacts,
    )

    with st.spinner("Researching..."):
        crew = get_crew(persona)
        output = crew.run(brief)

    st.session_state["last_output"] = output
    st.session_state["session_id"] = session_id

if "last_output" in st.session_state:
    st.divider()
    st.subheader("Research Results")
    for artifact in st.session_state["last_output"].artifacts:
        render_artifact(artifact)
