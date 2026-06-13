# infrastructure/artifact_exporter.py
from typing import Dict, Any, List
from infrastructure.citation_formatter import format_citation_list

def export_artifact(artifact: Dict[str, Any]) -> str:
    content = artifact.get("content", "")
    citations = artifact.get("citations", [])
    citation_block = f"\n\n---\n**Sources**\n{format_citation_list(citations)}" if citations else ""
    return f"{content}{citation_block}"

def export_all_artifacts(artifacts: List[Dict[str, Any]]) -> Dict[str, str]:
    result = {}
    for a in artifacts:
        key = a["type"]
        if key in result:
            i = 2
            while f"{key}_{i}" in result:
                i += 1
            key = f"{key}_{i}"
        result[key] = export_artifact(a)
    return result
