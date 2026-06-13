# infrastructure/artifact_exporter.py
from typing import Dict, Any, List
from infrastructure.citation_formatter import format_citation_list

def export_artifact(artifact: Dict[str, Any]) -> str:
    content = artifact.get("content", "")
    citations = artifact.get("citations", [])
    citation_block = f"\n\n---\n**Sources**\n{format_citation_list(citations)}" if citations else ""
    return f"{content}{citation_block}"

def export_all_artifacts(artifacts: List[Dict[str, Any]]) -> Dict[str, str]:
    return {a["type"]: export_artifact(a) for a in artifacts}
