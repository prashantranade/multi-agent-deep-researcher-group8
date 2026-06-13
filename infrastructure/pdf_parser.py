# infrastructure/pdf_parser.py
from pypdf import PdfReader
from docx import Document

def parse_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def parse_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

def parse_uploaded_file(file_path: str, mime_type: str) -> str:
    if mime_type == "application/pdf":
        return parse_pdf(file_path)
    elif mime_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ):
        return parse_docx(file_path)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()
