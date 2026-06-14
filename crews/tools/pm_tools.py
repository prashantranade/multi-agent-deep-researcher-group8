import json
from datetime import date

from langchain_core.tools import tool

from crews.product_manager.retrieval_agent import PMRetrievalAgent
from crews.product_manager.analysis_agent import PMAnalysisAgent
from crews.product_manager.output_agent import PMOutputAgent
from crews.tools.tool_context import get_runtime
from source_engine.scraper import scrape_selected_sources
from infrastructure.vector_store import VectorStore

_TABLE_NAME = "pm_research"


@tool
def scrape_and_index_market_sources() -> str:
    """Scrape the user's selected market research URLs, chunk the text, and embed chunks into the LanceDB product manager index. Call this first before searching for market research chunks."""
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
            "date": date.today().isoformat(),
        })
    if texts:
        store = VectorStore(db_path=runtime.db_path)
        store.drop_table(_TABLE_NAME)
        store.add_texts(texts, metadatas, table_name=_TABLE_NAME)
    return f"Indexed {len(texts)} text chunks from {len(enriched)} sources."


@tool
def search_market_research_chunks() -> str:
    """Run semantic search over the indexed product manager research table and return relevant market research chunks. Call after scrape_and_index_market_sources."""
    runtime = get_runtime()
    brief = runtime.brief
    query = f"{brief.topic} market size competition user pain points data"
    runtime.retrieved = VectorStore(db_path=runtime.db_path).search(
        query, table_name=_TABLE_NAME, k=10
    )
    return json.dumps({"chunk_count": len(runtime.retrieved), "chunks": runtime.retrieved[:3]})


@tool
def analyse_market_strategy() -> str:
    """Analyse indexed market research chunks for product strategy: market size, competitors, user pain points, opportunity, contradictions, and key data points. Returns JSON. Requires search_market_research_chunks to have run first."""
    runtime = get_runtime()
    if not runtime.retrieved:
        return "Error: no research chunks available. Call search_market_research_chunks first."
    runtime.analysis = PMAnalysisAgent().analyse(runtime.retrieved)
    return json.dumps(runtime.analysis)


@tool
def generate_pm_artifact(artifact_type: str) -> str:
    """Generate one product manager artifact from the completed analysis. artifact_type must be one of: research_brief, competitive_summary, opportunity_sizing, prd_insights."""
    runtime = get_runtime()
    if not runtime.analysis:
        return "Error: no analysis available. Call analyse_market_strategy first."
    target = artifact_type or runtime.artifact_type
    if not target:
        return "Error: artifact_type is required."
    artifacts = PMOutputAgent().generate_artifacts(runtime.analysis, [target])
    if not artifacts:
        return f"Error: unknown or unsupported artifact_type '{target}'."
    runtime.artifacts.extend(artifacts)
    return json.dumps(artifacts[0])


PM_RETRIEVE_TOOLS = [scrape_and_index_market_sources, search_market_research_chunks]
PM_ANALYSE_TOOLS = [analyse_market_strategy]
PM_GENERATE_TOOLS = [generate_pm_artifact]


def fallback_retrieve(db_path: str) -> list:
    """Direct retrieval when ReAct does not populate chunks."""
    runtime = get_runtime()
    runtime.retrieved = PMRetrievalAgent(db_path=db_path).retrieve(
        runtime.brief, runtime.brief.selected_sources
    )
    return runtime.retrieved
