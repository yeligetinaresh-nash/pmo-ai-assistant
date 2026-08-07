from pathlib import Path

from app.ai.extractor import (
    extract_pdf_text,
    extract_docx_text,
)


def parse_document(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension == ".docx":
        return extract_docx_text(file_path)

    raise ValueError(f"Unsupported file type: {extension}")