# intake/context_enrichment.py
import tempfile
import os
from typing import Optional
from source_engine.scraper import scrape_url
from infrastructure.pdf_parser import parse_uploaded_file
from infrastructure.image_analyser import analyse_image

def enrich_from_url(url: str) -> str:
    return scrape_url(url)[:3000]

def enrich_from_file(file_bytes: bytes, filename: str, mime_type: str) -> str:
    suffix = f".{filename.rsplit('.', 1)[-1]}" if "." in filename else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    try:
        if mime_type.startswith("image/"):
            return analyse_image(tmp_path)
        return parse_uploaded_file(tmp_path, mime_type)[:3000]
    finally:
        os.unlink(tmp_path)

def enrich_from_handle(handle: str) -> str:
    # Social handle enrichment — for hackathon, scrape profile URL or return handle as context
    cleaned = handle.lstrip("@")
    return f"Social media creator handle: @{cleaned}. Research should be tailored to this creator's style."

def build_context_text(
    url_text: str = "",
    file_text: str = "",
    handle_text: str = "",
) -> str:
    parts = []
    if url_text: parts.append(f"Website content:\n{url_text}")
    if file_text: parts.append(f"Uploaded document:\n{file_text}")
    if handle_text: parts.append(f"Social context:\n{handle_text}")
    return "\n\n".join(parts)
