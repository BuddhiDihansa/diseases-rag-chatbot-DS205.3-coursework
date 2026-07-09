import os
from typing import List, Dict, Any
import fitz  # PyMuPDF - pip install pymupdf


class PDFLoader:
    
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
        """
        Extract all text from a single PDF file page-by-page.
        Includes layout-aware sorting and built-in table extraction.
        """
        combined_document_text = []
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            filename = os.path.basename(pdf_path)
            
            for page_index, page in enumerate(doc):
                page_number = page_index + 1
                print(f"  --> Ingesting {filename} | Page {page_number}/{total_pages}...", end="\r")
                
                # 1. Super-fast sorted text extraction layout mapping
                text = page.get_text("text", sort=True) or ""
                
                # 2. Extract structural visual table matrices natively
                tables_data = []
                try:
                    tables = page.find_tables()
                    for table in tables:
                        tables_data.append(table.extract())
                except Exception:
                    tables_data = []
                
                # 3. Standardize and merge table string formats
                table_text = self._convert_tables_to_text(tables_data)
                page_text = self._merge_content(text, table_text)
                
                if page_text.strip():
                    combined_document_text.append(page_text)
                    
            doc.close()
            print(f"\n[Success] Fully extracted: {filename}")
        except Exception as e:
            print(f"\nError reading {pdf_path}: {e}")
            
        return "\n\n".join(combined_document_text)

    def load_all_pdfs(self) -> Dict[str, str]:
        """
        Load and extract text from all PDFs in the folder.
        Returns: { "disease_name.pdf": "extracted text..." }
        """
        pdf_files = self.list_pdf_files()
        results = {}

        for pdf_path in sorted(pdf_files):
            filename = os.path.basename(pdf_path)
            text = self.extract_text_from_pdf(pdf_path)
            results[filename] = text

        return results

    @staticmethod
    def _convert_tables_to_text(tables: list) -> str:
        """Converts raw table grid list profiles into clean markdown text rows."""
        if not tables:
            return ""
        rows = []
        for table in tables:
            for row in table:
                if row:
                    cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                    rows.append(" | ".join(cleaned_row))
        return "\n".join(rows)

    @staticmethod
    def _merge_content(text: str, table_text: str) -> str:
        """Merges native page text and extracted markdown table representations."""
        if text and table_text:
            return f"{text}\n\n[TABLE DATA]\n{table_text}"
        return text or table_text


# Example usage (for testing this file individually)
if __name__ == "__main__":
    # Create a dummy folder for a local test if needed
    os.makedirs("data/raw_pdfs", exist_ok=True)
    
    loader = PDFLoader(pdf_folder="data/raw_pdfs")
    print("--- PDF Directory Scan Test ---")
    try:
        all_texts = loader.load_all_pdfs()
        print(f"\nSuccessfully completed scan loop. Extracted {len(all_texts)} documents.")
    except Exception as e:
        print(f"Status check: {e} (Add real PDFs to 'data/raw_pdfs' to test full layout loading)")