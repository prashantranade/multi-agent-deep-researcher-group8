# infrastructure/citation_formatter.py
from typing import List, Dict

def format_citation(source: Dict, index: int) -> str:
    title = source.get("title", "Untitled")
    url = source.get("url", "")
    domain = source.get("domain", "")
    date = source.get("date", "n.d.")
    return f"[{index}] {title} — {domain} ({date})\n    {url}"

def format_citation_list(sources: List[Dict]) -> str:
    return "\n".join(format_citation(s, i + 1) for i, s in enumerate(sources))
