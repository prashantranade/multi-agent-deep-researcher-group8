# ui/artifact_renderer.py
from typing import Dict, Any

_RENDER_CONFIGS = {
    # BharatDesha primary content
    "blog_post":            {"label": "Blog Post",            "display": "markdown"},
    "itinerary":            {"label": "Itinerary",             "display": "markdown"},
    "destination_guide":    {"label": "Destination Guide",     "display": "markdown"},
    "wellness_guide":       {"label": "Wellness Guide",        "display": "markdown"},
    # BharatDesha social
    "instagram":            {"label": "Instagram Caption",     "display": "text_box"},
    "facebook":             {"label": "Facebook Post",         "display": "text_box"},
    "x_post":               {"label": "X (Twitter) Thread",   "display": "text_box"},
    "youtube":              {"label": "YouTube Metadata",      "display": "sections"},
    "seo_keywords":         {"label": "SEO Keywords",          "display": "markdown"},
    # Content Creator artifacts
    "content_brief":        {"label": "Content Brief",         "display": "markdown"},
    "social_post":          {"label": "Social Post",           "display": "text_box"},
    "newsletter":           {"label": "Newsletter",            "display": "markdown"},
    # Product Manager artifacts
    "competitive_analysis": {"label": "Competitive Analysis",  "display": "markdown"},
    "product_roadmap":      {"label": "Product Roadmap",       "display": "markdown"},
    "user_research":        {"label": "User Research",         "display": "markdown"},
    "executive_summary":    {"label": "Executive Summary",     "display": "markdown"},
}

_DEFAULT_CONFIG = {"label": "Output", "display": "markdown"}

def get_render_config(artifact_type: str) -> Dict[str, str]:
    return _RENDER_CONFIGS.get(artifact_type, _DEFAULT_CONFIG)

def render_artifact(artifact: Dict[str, Any]) -> None:
    """Render a single artifact dict to Streamlit. Must be called from a Streamlit context."""
    import streamlit as st

    artifact_type = artifact.get("type", "unknown")
    content = artifact.get("content", "")
    citations = artifact.get("citations", [])
    cfg = get_render_config(artifact_type)

    st.subheader(cfg["label"])

    if cfg["display"] == "markdown":
        st.markdown(content)
    elif cfg["display"] == "text_box":
        st.text_area(cfg["label"], value=content, height=200, key=f"artifact_{artifact_type}_{id(artifact)}")
    elif cfg["display"] == "sections":
        # YouTube: parse TITLE / DESCRIPTION / CHAPTERS sections
        sections = {"TITLE": "", "DESCRIPTION": "", "CHAPTERS": ""}
        current = None
        for line in content.splitlines():
            if line.startswith("TITLE:"):
                current = "TITLE"
                sections["TITLE"] = line[6:].strip()
            elif line.startswith("DESCRIPTION:"):
                current = "DESCRIPTION"
                sections["DESCRIPTION"] = line[12:].strip()
            elif line.startswith("CHAPTERS:"):
                current = "CHAPTERS"
            elif current == "DESCRIPTION":
                sections["DESCRIPTION"] += "\n" + line
            elif current == "CHAPTERS":
                sections["CHAPTERS"] += line + "\n"
        st.text_input("Title", value=sections["TITLE"])
        st.text_area("Description", value=sections["DESCRIPTION"].strip(), height=150)
        st.text_area("Chapters", value=sections["CHAPTERS"].strip(), height=100)

    if citations:
        with st.expander("Sources"):
            for url in citations:
                st.markdown(f"- {url}")
