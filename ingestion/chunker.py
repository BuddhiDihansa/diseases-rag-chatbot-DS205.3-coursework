from typing import List, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class Chunk:
    
    chunk_id: str
    text: str
    source_document: str
    chunk_index: int


# Patterns that reliably identify front-matter/administrative content:
# title pages, forewords ("Message from the Director..."), ISBN/
# copyright notices, and tables of contents. These chunks carry no
# clinical information, but they still surface in vector/BM25 search
# because they repeat the disease name in formal prose (e.g. "dengue
# continues to be a major health problem") - which was observed
# crowding out genuinely relevant clinical chunks from the retrieved
# top-k (see evaluation notes / Report Section III for the specific
# example: a Director's foreword message outranked the actual DF/DHF
# clinical case-definition chunk for "What are the symptoms of Dengue
# fever?").
_BOILERPLATE_PATTERNS = [
    re.compile(r'\bMessage from the\b', re.IGNORECASE),
    re.compile(r'\bISBN\b'),
    re.compile(r'^\s*Contents\s*$', re.IGNORECASE | re.MULTILINE),
]

# A committee/acknowledgements list chunk typically contains several
# "Dr <Name>" / "Prof <Name>" occurrences in a short span - real
# clinical text almost never does.
_NAME_TITLE_PATTERN = re.compile(r'\b(?:Dr|Prof)\s[A-Z][a-zA-Z\']+(?:\s[A-Z][a-zA-Z\']+)?')


def is_boilerplate_chunk(text: str) -> bool:
    """
    Heuristically flags front-matter/administrative chunks so they can
    be excluded from the corpus before embedding. See _BOILERPLATE_
    PATTERNS docstring above for why this matters for retrieval
    quality, not just corpus tidiness.
    """
    if any(pattern.search(text) for pattern in _BOILERPLATE_PATTERNS):
        return True

    name_title_hits = len(_NAME_TITLE_PATTERN.findall(text))
    return name_title_hits >= 3


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

        # 3b. Drop front-matter/administrative chunks (title pages,
        # committee/acknowledgements lists, forewords, ISBN/TOC pages)
        # before they get embedded - see is_boilerplate_chunk() docstring.
        kept_chunks = []
        dropped_count = 0
        for c in dataclass_chunks:
            if is_boilerplate_chunk(c.text):
                dropped_count += 1
            else:
                kept_chunks.append(c)

        if dropped_count:
            print(f"  [Chunker] Filtered out {dropped_count} boilerplate/"
                  f"front-matter chunks out of {len(dataclass_chunks)} total.")
        dataclass_chunks = kept_chunks

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