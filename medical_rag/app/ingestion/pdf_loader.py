"""PDF ingestion using PyMuPDF with overlapping chunking."""
import fitz  # PyMuPDF
from typing import List, Dict
from app.ingestion.base import BaseIngester


class PDFIngester(BaseIngester):
    """
    Loads PDFs via PyMuPDF, extracts text page-by-page,
    and splits into overlapping chunks for optimal RAG retrieval.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """
        Args:
            chunk_size: Number of characters per chunk.
            chunk_overlap: Overlap between consecutive chunks (prevents context loss).
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load(self, source: str) -> List[Dict]:
        """
        Open a PDF file and extract all text, then chunk it.

        Args:
            source: File path string to the PDF.

        Returns:
            List of chunk dicts with 'text' and 'metadata'.
        """
        doc = fitz.open(source)
        all_chunks = []

        for page_num, page in enumerate(doc):
            page_text = page.get_text("text").strip()
            if not page_text:
                continue  # skip empty/image-only pages

            metadata = {
                "source": source,
                "page": page_num + 1,
                "total_pages": len(doc),
            }
            chunks = self.chunk(page_text, metadata)
            all_chunks.extend(chunks)

        doc.close()
        return all_chunks

    def load_from_bytes(self, file_bytes: bytes, filename: str) -> List[Dict]:
        """
        Load a PDF from raw bytes (for Streamlit file upload).

        Args:
            file_bytes: Raw PDF bytes from st.file_uploader.
            filename: Original filename for metadata.

        Returns:
            List of chunk dicts.
        """
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        all_chunks = []

        for page_num, page in enumerate(doc):
            page_text = page.get_text("text").strip()
            if not page_text:
                continue

            metadata = {
                "source": filename,
                "page": page_num + 1,
                "total_pages": len(doc),
            }
            chunks = self.chunk(page_text, metadata)
            all_chunks.extend(chunks)

        doc.close()
        return all_chunks

    def chunk(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Split text into overlapping chunks using a sliding window.

        Args:
            text: Full page/document text.
            metadata: Metadata to attach to each chunk.

        Returns:
            List of chunk dicts.
        """
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {**metadata, "chunk_start": start, "chunk_end": end},
                })

            # Move forward by (chunk_size - overlap) to create sliding window
            start += self.chunk_size - self.chunk_overlap

        return chunks
