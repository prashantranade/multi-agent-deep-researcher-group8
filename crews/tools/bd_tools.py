import json

from langchain_core.tools import tool

from crews.bharat_desha.retrieval_agent import run_retrieval_agent
from crews.bharat_desha.analysis_agent import run_analysis_agent
from crews.bharat_desha.content_agent import run_content_agent
from crews.bharat_desha.social_agent import run_social_agent
from crews.tools.tool_context import get_runtime

_SOCIAL_PLATFORMS = {"instagram", "facebook", "x_post", "youtube"}
_PRIMARY_CONTENT_TYPES = {"blog_post", "itinerary", "destination_guide", "wellness_guide"}


@tool
def search_and_index_travel_research() -> str:
    """Search Tavily for India travel research on the topic, index chunks into the LanceDB bharat_desha table, and load relevant chunks. Requires SEO context from upstream. Call this in the retrieval phase."""
    runtime = get_runtime()
    runtime.retrieved = run_retrieval_agent(runtime.brief.topic, runtime.seo_context or {})
    return json.dumps({"chunk_count": len(runtime.retrieved), "chunks": runtime.retrieved[:3]})


@tool
def analyse_bharat_desha_research() -> str:
    """Analyse retrieved travel research through the BharatDesha lens: spiritual significance, practical logistics, cultural authenticity, wellness, and seasonal timing. Returns JSON. Requires search_and_index_travel_research first."""
    runtime = get_runtime()
    if not runtime.retrieved:
        return "Error: no research chunks available. Call search_and_index_travel_research first."
    runtime.analysis = run_analysis_agent(
        runtime.retrieved,
        runtime.seo_context or {},
        runtime.trend_context or {},
    )
    return json.dumps(runtime.analysis)


@tool
def generate_primary_travel_content(artifact_type: str) -> str:
    """Generate the primary BharatDesha content artifact. artifact_type must be one of: blog_post, itinerary, destination_guide, wellness_guide."""
    runtime = get_runtime()
    if not runtime.analysis:
        return "Error: no analysis available. Call analyse_bharat_desha_research first."
    target = artifact_type or runtime.artifact_type
    if not target or target not in _PRIMARY_CONTENT_TYPES:
        return f"Error: artifact_type must be one of {sorted(_PRIMARY_CONTENT_TYPES)}."
    artifact = run_content_agent(
        runtime.analysis,
        runtime.seo_context or {},
        artifact_type=target,
        tone=runtime.brief.tone,
        depth=runtime.brief.depth,
    )
    runtime.primary_artifact = artifact
    runtime.artifacts.append(artifact)
    return json.dumps(artifact)


@tool
def generate_social_travel_content(platform: str) -> str:
    """Repurpose primary content for a social platform. platform must be one of: instagram, facebook, x_post, youtube. Requires generate_primary_travel_content first."""
    runtime = get_runtime()
    if not runtime.primary_artifact:
        return "Error: no primary content available. Call generate_primary_travel_content first."
    if platform not in _SOCIAL_PLATFORMS:
        return f"Error: platform must be one of {sorted(_SOCIAL_PLATFORMS)}."
    artifacts = run_social_agent(
        runtime.primary_artifact,
        runtime.analysis.get("key_points", []),
        runtime.seo_context or {},
        platforms=[platform],
    )
    if not artifacts:
        return f"Error: failed to generate content for platform '{platform}'."
    runtime.artifacts.extend(artifacts)
    return json.dumps(artifacts[0])


BD_RETRIEVE_TOOLS = [search_and_index_travel_research]
BD_ANALYSE_TOOLS = [analyse_bharat_desha_research]
BD_GENERATE_TOOLS = [generate_primary_travel_content, generate_social_travel_content]


def fallback_retrieve() -> list:
    """Direct retrieval when ReAct does not populate chunks."""
    runtime = get_runtime()
    runtime.retrieved = run_retrieval_agent(runtime.brief.topic, runtime.seo_context or {})
    return runtime.retrieved


def seo_keywords_artifact(seo_context: dict) -> dict:
    keyword_lines = "\n".join(
        f"{i + 1}. {k['keyword']} ({k['intent']})"
        for i, k in enumerate(seo_context.get("keywords", []))
    )
    return {"type": "seo_keywords", "content": keyword_lines, "citations": []}
