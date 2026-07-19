"""
services/resume_parser.py
--------------------------
Extracts raw text from an uploaded PDF resume using PyPDF2, so it can be
handed to the AI service (or the mock analyzer) for evaluation.
"""

from pypdf import PdfReader


def extract_text_from_pdf(filepath):
    """Return the concatenated text of all pages in the PDF at `filepath`.
    Returns an empty string if the PDF has no extractable text (e.g. scanned
    image-only PDFs), rather than raising, so callers can handle that gracefully.
    """
    try:
        reader = PdfReader(filepath)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception:
        return ""
