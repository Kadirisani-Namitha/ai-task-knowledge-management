import logging
import os

import fitz  # PyMuPDF
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def extract_text(file_path: str, file_type: str) -> str:
    file_type = file_type.lower()
    if file_type == "pdf":
        return _extract_pdf(file_path)
    elif file_type == "docx":
        return _extract_docx(file_path)
    elif file_type == "txt":
        return _extract_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def _extract_pdf(path: str) -> str:
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n".join(pages)


def _extract_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """
    Split text into overlapping chunks of approximately `chunk_size` characters.
    Splitting is done on whitespace boundaries to avoid cutting words.
    """
    text = text.strip()
    if not text:
        return []

    words = text.split()
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for word in words:
        word_len = len(word) + 1  # +1 for the space
        if current_length + word_len > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            # Keep the last `overlap` characters worth of words
            overlap_words: list[str] = []
            overlap_len = 0
            for w in reversed(current_chunk):
                if overlap_len + len(w) + 1 > overlap:
                    break
                overlap_words.insert(0, w)
                overlap_len += len(w) + 1
            current_chunk = overlap_words
            current_length = overlap_len
        current_chunk.append(word)
        current_length += word_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
