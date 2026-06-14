import json

from langchain_core.tools import tool

from crews.content_creator.retrieval_agent import CCRetrievalAgent
from crews.content_creator.analysis_agent import CCAnalysisAgent
from crews.content_creator.output_agent import CCOutputAgent
from crews.tools.tool_context import get_runtime
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore


@tool
def scrape_and_index_sources() -> str:
    """Scrape the user's selected research URLs, chunk the text, and embed chunks into the LanceDB content creator index. Call this first before searching for research chunks."""
    runtime = get_runtime()
    brief = runtime.brief
    enriched = scrape_selected_sources(brief.selected_sources)
    texts, metadatas = [], []
    for src in enriched:
        if src["content"]:
            chunks = [src["content"][i : i + 1000] for i in range(0, len(src["content"]), 1000)]
            for chunk in chunks[:5]:
                texts.append(chunk)
                metadatas.append({
                    "source": src["url"],
                    "title": src["title"],
                    "domain": src["domain"],
                    "date": src["date"],
                })
    if brief.context_text:
        texts.append(brief.context_text)
        metadatas.append({
            "source": "user_context",
            "title": "User context",
            "domain": "user",
            "date": "2026-01-01",
        })
    if texts:
        VectorStore(db_path=runtime.db_path).add_texts(texts, metadatas, table_name="cc_research")
    return f"Indexed {len(texts)} text chunks from {len(enriched)} sources."


@tool
def search_research_chunks() -> str:
    """Run semantic search over the indexed content creator research table and return relevant text chunks for the research topic. Call after scrape_and_index_sources."""
    runtime = get_runtime()
    brief = runtime.brief
    query = f"{brief.topic} for {brief.audience} in {brief.tone} tone"
    runtime.retrieved = VectorStore(db_path=runtime.db_path).search(
        query, table_name="cc_research", k=10
    )
    return json.dumps({"chunk_count": len(runtime.retrieved), "chunks": runtime.retrieved[:3]})


@tool
def analyse_content_strategy() -> str:
    """Analyse indexed research chunks for content strategy: trends, hooks, audience signals, tone notes, and key facts. Returns JSON. Requires search_research_chunks to have run first."""
    runtime = get_runtime()
    if not runtime.retrieved:
        return "Error: no research chunks available. Call search_research_chunks first."
    runtime.analysis = CCAnalysisAgent().analyse(runtime.retrieved)
    return json.dumps(runtime.analysis)


@tool
def generate_content_artifact(artifact_type: str) -> str:
    """Generate one content artifact from the completed analysis. artifact_type must be one of: content_brief, social_draft, captions, hashtags, calendar_entry."""
    runtime = get_runtime()
    if not runtime.analysis:
        return "Error: no analysis available. Call analyse_content_strategy first."
    target = artifact_type or runtime.artifact_type
    if not target:
        return "Error: artifact_type is required."
    artifacts = CCOutputAgent().generate_artifacts(runtime.analysis, [target])
    if not artifacts:
        return f"Error: unknown or unsupported artifact_type '{target}'."
    runtime.artifacts.extend(artifacts)
    return json.dumps(artifacts[0])


CC_RETRIEVE_TOOLS = [scrape_and_index_sources, search_research_chunks]
CC_ANALYSE_TOOLS = [analyse_content_strategy]
CC_GENERATE_TOOLS = [generate_content_artifact]


def fallback_retrieve(db_path: str) -> list:
    """Direct retrieval when ReAct does not populate chunks."""
    runtime = get_runtime()
    runtime.retrieved = CCRetrievalAgent(db_path=db_path).retrieve(
        runtime.brief, runtime.brief.selected_sources
    )
    return runtime.retrieved
