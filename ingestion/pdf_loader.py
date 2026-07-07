"""
pdf_loader.py
Member 1 - Data Engineering

Purpose: Extract raw text from PDF files (disease documents from WHO/CDC/MOH)
"""

import os
from typing import List, Dict
import fitz  # PyMuPDF - pip install pymupdf


class PDFLoader:
    """
    Responsible for loading PDF files and extracting raw text.
    Uses Dependency Injection: pass in the folder path via constructor,
    not hardcoded, so it's easy to test and reuse.
    """

    def __init__(self, pdf_folder: str):
        self.pdf_folder = pdf_folder

    def list_pdf_files(self) -> List[str]:
        """Return list of all PDF file paths in the folder."""
        if not os.path.exists(self.pdf_folder):
            raise FileNotFoundError(f"Folder not found: {self.pdf_folder}")

        return [
            os.path.join(self.pdf_folder, f)
            for f in os.listdir(self.pdf_folder)
            if f.lower().endswith(".pdf")
        ]

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a single PDF file."""
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
        return text

    def load_all_pdfs(self) -> Dict[str, str]:
        """
        Load and extract text from all PDFs in the folder.
        Returns: { "disease_name.pdf": "extracted text..." }
        """
        pdf_files = self.list_pdf_files()
        results = {}

        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            print(f"Processing: {filename}")
            text = self.extract_text_from_pdf(pdf_path)
            results[filename] = text

        return results


# Example usage (for testing this file individually)
if __name__ == "__main__":
    loader = PDFLoader(pdf_folder="data/raw_pdfs")
    all_texts = loader.load_all_pdfs()

    for filename, text in all_texts.items():
        print(f"\n{filename}: {len(text)} characters extracted")