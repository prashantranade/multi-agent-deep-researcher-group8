# tests/test_parsers.py
import pytest
from unittest.mock import patch, MagicMock
from infrastructure.pdf_parser import parse_pdf, parse_docx, parse_uploaded_file
from infrastructure.image_analyser import analyse_image

def test_parse_pdf_returns_text():
    with patch("infrastructure.pdf_parser.PdfReader") as mock_reader:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Hello from PDF"
        mock_reader.return_value.pages = [mock_page]
        result = parse_pdf("fake.pdf")
    assert "Hello from PDF" in result

def test_parse_docx_returns_text():
    with patch("infrastructure.pdf_parser.Document") as mock_doc:
        mock_para = MagicMock()
        mock_para.text = "Hello from DOCX"
        mock_doc.return_value.paragraphs = [mock_para]
        result = parse_docx("fake.docx")
    assert "Hello from DOCX" in result

def test_parse_uploaded_file_pdf():
    with patch("infrastructure.pdf_parser.parse_pdf") as mock_pdf:
        mock_pdf.return_value = "PDF content"
        result = parse_uploaded_file("fake.pdf", "application/pdf")
    assert result == "PDF content"

def test_parse_uploaded_file_txt():
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("plain text content")
        tmp = f.name
    try:
        result = parse_uploaded_file(tmp, "text/plain")
        assert "plain text content" in result
    finally:
        os.unlink(tmp)

def test_analyse_image_returns_description():
    with patch("infrastructure.image_analyser.OpenAI") as mock_openai, \
         patch("infrastructure.image_analyser._encode_image") as mock_encode:
        mock_encode.return_value = "base64_encoded_data"
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = "A mountain landscape"
        result = analyse_image("fake_image.png")
    assert isinstance(result, str)
    assert len(result) > 0
