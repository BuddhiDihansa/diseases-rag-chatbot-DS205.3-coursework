from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    
    chunk_id: str
    text: str
    source_document: str
    chunk_index: int


class TextChunker:
    """
    Splits text into chunks with configurable size and overlap.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _snap_to_word_end(self, text: str, start: int, target_end: int) -> int:
        """Given a target end position, return the nearest whitespace position."""
        text_length = len(text)
        if target_end >= text_length:
            return text_length

        boundary = text.rfind(" ", start, target_end)
        newline_boundary = text.rfind("\n", start, target_end)
        boundary = max(boundary, newline_boundary)

        if boundary > start:
            return boundary
        return target_end

    def _snap_to_word_start(self, text: str, position: int) -> int:
        """Given a position, move forward to the start of the next whole word."""
        text_length = len(text)
        pos = position
        if pos <= 0 or pos >= text_length or text[pos - 1] in (" ", "\n", "\t"):
            return pos
        while pos < text_length and text[pos] not in (" ", "\n", "\t"):
            pos += 1
        while pos < text_length and text[pos] in (" ", "\n", "\t"):
            pos += 1
        return pos

    def chunk_text(self, text: str, source_document: str) -> List[Chunk]:
        """Split a single document's text into overlapping chunks, snapped to word boundaries."""
        chunks = []
        start = 0
        chunk_index = 0
        text_length = len(text)

        while start < text_length:
            target_end = start + self.chunk_size
            end = self._snap_to_word_end(text, start, target_end)

            chunk_text_content = text[start:end].strip()

            if chunk_text_content:
                chunk = Chunk(
                    chunk_id=f"{source_document}_chunk_{chunk_index}",
                    text=chunk_text_content,
                    source_document=source_document,
                    chunk_index=chunk_index
                )
                chunks.append(chunk)
                chunk_index += 1

            target_next_start = end - self.chunk_overlap
            if target_next_start <= start:
                target_next_start = end

            next_start = self._snap_to_word_start(text, target_next_start)
            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    def chunk_multiple_documents(self, documents: Dict[str, str]) -> List[Chunk]:
        """Chunk multiple documents at once."""
        all_chunks = []
        for doc_name, text in documents.items():
            doc_chunks = self.chunk_text(text, source_document=doc_name)
            all_chunks.extend(doc_chunks)
            print(f"  [Chunker] '{doc_name}': Generated {len(doc_chunks)} chunks.")

        return all_chunks


class DataProcessor:
    """
    Orchestrates the full data engineering ingestion pipeline:
    PDF Loader -> Text Cleaner -> Text Chunker -> File Serializer Export
    """

    def __init__(self, loader: Any, cleaner: Any, chunker: TextChunker):
        self._loader = loader
        self._cleaner = cleaner
        self._chunker = chunker

    def process_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """
        Runs the full loading, cleaning, and chunking pipeline over a directory.
        Transforms raw text maps into structured dictionaries for Member 2.
        """
        # Update the path folder variable dynamically inside the loader instance
        self._loader.pdf_folder = str(directory)
        
        # 1. Bulk load and extract sorted layout texts
        raw_documents = self._loader.load_all_pdfs()
        
        # 2. Clean text layers in-place
        cleaned_documents = {}
        for doc_name, raw_text in raw_documents.items():
            cleaned_documents[doc_name] = self._cleaner.clean(raw_text)
            
        # 3. Create overlapping word-snapped chunks
        dataclass_chunks = self._chunker.chunk_multiple_documents(cleaned_documents)
        
        # 4. Serialize objects into dictionary structures for Member 2's Vector Store
        serializable_payload = []
        for c in dataclass_chunks:
            serializable_payload.append({
                "chunk_id": c.chunk_id,
                "source_document": c.source_document,
                "chunk_index": c.chunk_index,
                "chunk_text": c.text
            })
            
        return serializable_payload


# Example usage (for testing this file individually)
if __name__ == "__main__":
    sample_text = ("Diabetes is a chronic disease that occurs when the pancreas is no "
                    "longer able to make insulin, or when the body cannot effectively "
                    "use the insulin it produces. ") * 10

    chunker = TextChunker(chunk_size=200, chunk_overlap=30)
    chunks = chunker.chunk_text(sample_text, source_document="diabetes.pdf")

    print("--- Chunker Slicing Test ---")
    print(f"Created {len(chunks)} chunks\n")
    if chunks:
        print(f"{chunks[0].chunk_id}:")
        print(f"  starts: '{chunks[0].text[:40]}...'")
        print(f"  ends:   '...{chunks[0].text[-40:]}'\n")

