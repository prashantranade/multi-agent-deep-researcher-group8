# source_engine/confidence_scorer.py
from datetime import datetime
from typing import List, Dict, Any

TRUSTED_DOMAINS = {
    "bbc.com", "reuters.com", "nytimes.com", "theguardian.com", "bloomberg.com",
    "economist.com", "nature.com", "sciencedirect.com", "pubmed.ncbi.nlm.nih.gov",
    "hbr.org", "mckinsey.com", "wikipedia.org", "britannica.com",
    "gov.in", "nic.in", "who.int", "worldbank.org",
}

def _recency_score(date_str: str) -> float:
    try:
        pub_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        days_old = (datetime.now() - pub_date).days
        if days_old <= 90: return 1.0
        if days_old <= 365: return 0.8
        if days_old <= 730: return 0.6
        if days_old <= 1825: return 0.4
        return 0.2
    except Exception:
        return 0.3

def _domain_score(domain: str) -> float:
    clean = domain.replace("www.", "")
    for trusted in TRUSTED_DOMAINS:
        if clean == trusted or clean.endswith(f".{trusted}"):
            return 1.0
    if clean.endswith((".gov", ".edu", ".ac.uk", ".ac.in")):
        return 0.9
    if clean.endswith((".org", ".int")):
        return 0.7
    return 0.5

def _relevance_score(snippet: str) -> float:
    word_count = len(snippet.split())
    if word_count >= 200: return 1.0
    if word_count >= 100: return 0.8
    if word_count >= 50: return 0.6
    if word_count >= 10: return 0.4
    return 0.2

def score_source(source: Dict[str, Any]) -> Dict[str, Any]:
    recency = _recency_score(source.get("date", ""))
    domain = _domain_score(source.get("domain", ""))
    relevance = _relevance_score(source.get("snippet", ""))
    overall = round((recency * 0.3) + (domain * 0.4) + (relevance * 0.3), 2)
    return {**source, "recency_score": recency, "domain_score": domain, "relevance_score": relevance, "overall_score": overall}

def score_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored = [score_source(s) for s in sources]
    return sorted(scored, key=lambda x: x["overall_score"], reverse=True)
