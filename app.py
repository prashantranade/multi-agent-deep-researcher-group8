
# app.py
import streamlit as st
import uuid
from intake.clarification_agent import ClarificationAgent
from intake.context_enrichment import enrich_from_url, enrich_from_file, enrich_from_handle, build_context_text
from source_engine.discovery import discover_sources
from source_engine.confidence_scorer import score_sources
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore
from infrastructure.artifact_exporter import export_artifact
from observability.langfuse_client import get_langfuse_handler
import config

# Lazy import crews so squads can work independently
def _load_crew(persona: str):
    if persona == "content_creator":
        from crews.content_creator.retrieval_agent import CCRetrievalAgent
        from crews.content_creator.analysis_agent import CCAnalysisAgent
        from crews.content_creator.output_agent import CCOutputAgent
        class CCCrew:
            def __init__(self):
                self.retrieval = CCRetrievalAgent()
                self.analysis = CCAnalysisAgent()
                self.output = CCOutputAgent()
            def run(self, brief):
                retrieved = self.retrieval.retrieve(brief, brief.selected_sources)
                analysis = self.analysis.analyse(retrieved)
                return self.output.generate_artifacts(analysis, brief.selected_artifacts)
        return CCCrew()
    elif persona == "product_manager":
        from crews.product_manager.retrieval_agent import PMRetrievalAgent
        from crews.product_manager.analysis_agent import PMAnalysisAgent
        from crews.product_manager.output_agent import PMOutputAgent
        class PMCrew:
            def __init__(self):
                self.retrieval = PMRetrievalAgent()
                self.analysis = PMAnalysisAgent()
                self.output = PMOutputAgent()
            def run(self, brief):
                retrieved = self.retrieval.retrieve(brief, brief.selected_sources)
                analysis = self.analysis.analyse(retrieved)
                return self.output.generate_artifacts(analysis, brief.selected_artifacts)
        return PMCrew()

st.set_page_config(page_title="Deep Researcher", layout="wide")
st.title("Multi-Agent Deep Researcher")
st.caption("Persona-aware · source-verified · multimodal")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "context_text" not in st.session_state:
    st.session_state.context_text = ""
if "brief" not in st.session_state:
    st.session_state.brief = None
if "sources" not in st.session_state:
    st.session_state.sources = []

# ── STEP 1: Persona ──────────────────────────────────────────────────────────
with st.expander("Step 1 — Select your persona", expanded=st.session_state.step == 1):
    persona = st.radio("I am a...", ["Content Creator", "Product Manager"], horizontal=True)
    if st.button("Continue →", key="step1"):
        st.session_state.persona = "content_creator" if "Creator" in persona else "product_manager"
        st.session_state.step = 2
        st.rerun()

# ── STEP 2: Topic ─────────────────────────────────────────────────────────────
if st.session_state.step >= 2:
    with st.expander("Step 2 — What do you want to research?", expanded=st.session_state.step == 2):
        topic = st.text_input("Research topic", placeholder="e.g. Sustainable travel in Rajasthan for millennials")
        if st.button("Continue →", key="step2") and topic:
            st.session_state.topic = topic
            st.session_state.step = 3
            st.rerun()

# ── STEP 3: Context enrichment ───────────────────────────────────────────────
if st.session_state.step >= 3:
    with st.expander("Step 3 — Add context (optional)", expanded=st.session_state.step == 3):
        url_input = st.text_input("Your website or relevant URL", placeholder="https://bharatdesha.com")
        handle_input = st.text_input("Social media handle", placeholder="@bharatdesha")
        uploaded_files = st.file_uploader("Upload documents or images", accept_multiple_files=True,
                                          type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
        if st.button("Continue →", key="step3"):
            url_text = enrich_from_url(url_input) if url_input else ""
            handle_text = enrich_from_handle(handle_input) if handle_input else ""
            file_texts = []
            for f in (uploaded_files or []):
                file_texts.append(enrich_from_file(f.read(), f.name, f.type))
            file_text = "\n\n".join(file_texts)
            st.session_state.context_text = build_context_text(url_text, file_text, handle_text)
            st.session_state.step = 4
            st.rerun()

# ── STEP 4: Clarification ─────────────────────────────────────────────────────
if st.session_state.step >= 4:
    with st.expander("Step 4 — A few quick questions", expanded=st.session_state.step == 4):
        agent = ClarificationAgent()
        question = agent.get_next_question(
            st.session_state.topic,
            st.session_state.persona,
            st.session_state.context_text,
            st.session_state.answers,
        )
        if question:
            answer = st.text_input(question, key=f"q_{question[:20]}")
            if st.button("Next →", key="clarify_next") and answer:
                for field in ["audience", "tone", "depth"]:
                    if field not in st.session_state.answers:
                        st.session_state.answers[field] = answer
                        break
                st.rerun()
        else:
            st.success("Brief complete. Ready to discover sources.")
            if st.button("Discover sources →", key="step4"):
                brief = agent.build_brief(
                    st.session_state.topic,
                    st.session_state.persona,
                    st.session_state.context_text,
                    st.session_state.answers,
                )
                st.session_state.brief = brief
                with st.spinner("Discovering sources..."):
                    raw = discover_sources(st.session_state.topic)
                    st.session_state.sources = score_sources(raw)
                st.session_state.step = 5
                st.rerun()

# ── STEP 5: Source curation ───────────────────────────────────────────────────
if st.session_state.step >= 5:
    with st.expander("Step 5 — Select your sources", expanded=st.session_state.step == 5):
        st.caption("Scored by recency · domain authority · relevance. Select sources you trust.")
        selected = []
        for src in st.session_state.sources:
            col1, col2 = st.columns([3, 1])
            with col1:
                checked = st.checkbox(f"**{src['title']}** — {src['domain']} ({src['date']})", key=src["url"])
                if checked:
                    selected.append(src)
            with col2:
                st.caption(f"Score: {src['overall_score']:.0%}")
        if st.button("Confirm sources →", key="step5") and selected:
            st.session_state.brief.selected_sources = selected
            st.session_state.step = 6
            st.rerun()

# ── STEP 6: Artifact selection ────────────────────────────────────────────────
if st.session_state.step >= 6:
    with st.expander("Step 6 — What do you want out?", expanded=st.session_state.step == 6):
        persona = st.session_state.persona
        if persona == "content_creator":
            options = ["content_brief", "social_draft", "captions", "hashtags", "calendar_entry"]
        else:
            options = ["research_brief", "competitive_summary", "opportunity_sizing", "prd_insights"]
        selected_artifacts = st.multiselect("Select artifacts to generate", options, default=[options[0]])
        if st.button("Run research agents →", key="step6") and selected_artifacts:
            st.session_state.brief.selected_artifacts = selected_artifacts
            st.session_state.step = 7
            st.rerun()

# ── STEP 7: Agent run + output ────────────────────────────────────────────────
if st.session_state.step >= 7:
    with st.expander("Step 7 — Research results", expanded=True):
        if "artifacts" not in st.session_state:
            with st.spinner("Agent crew working... (this takes 30–60 seconds)"):
                try:
                    crew = _load_crew(st.session_state.persona)
                    artifacts = crew.run(st.session_state.brief)
                    st.session_state.artifacts = artifacts
                except Exception as e:
                    st.error(f"Agent error: {e}")
                    st.stop()
        for artifact in st.session_state.get("artifacts", []):
            st.subheader(artifact["type"].replace("_", " ").title())
            exported = export_artifact(artifact)
            st.markdown(exported)
            st.download_button(
                f"Download {artifact['type']}",
                exported,
                file_name=f"{artifact['type']}.md",
                key=f"dl_{artifact['type']}",
            )
        if st.button("Start new research", key="restart"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

