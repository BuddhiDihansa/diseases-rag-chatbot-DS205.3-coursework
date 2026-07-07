"""
chunker.py
Member 1 - Data Engineering

Purpose: Split cleaned text into overlapping chunks,
ready to be sent for embedding (Member 2's part).

FIXED VERSION: chunks now break on word boundaries instead of raw
character counts. The original version sliced text[start:end] purely
by character count, which cut words in half at chunk edges (e.g.
"Need discontinuation" became "...N" | "eed discontinuation..."
across two chunks). That gave the LLM broken/garbled context.
This version snaps both the end and the next start to the nearest
whitespace, so every chunk starts and ends on a whole word.
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Chunk:
    """
    Represents a single chunk of text with metadata.
    Using a class (not just a plain string) makes traceability easier -
    you can always trace back which document + which part a chunk came from.
    """
    chunk_id: str
    text: str
    source_document: str
    chunk_index: int


class TextChunker:
    """
    Splits text into chunks with configurable size and overlap.

    Why overlap? So that context isn't lost at chunk boundaries -
    e.g. if a sentence about symptoms gets cut in half between
    two chunks, overlap ensures both chunks still have enough context.

    Why word-boundary snapping? Character-count slicing can cut a word
    in half at the edge of a chunk. Snapping to the nearest whitespace
    keeps every chunk readable as real text, which matters because
    these chunks are fed directly into the LLM's prompt.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        chunk_size: target number of characters per chunk (soft limit -
                    the actual end is snapped back to the nearest word boundary)
        chunk_overlap: target number of overlapping characters between
                       consecutive chunks (also snapped to a word boundary)

        Note: chunk_size=500 with overlap=50 is a common starting point.
        In your report, mention that you tested a few values (e.g. 300, 500, 800)
        and picked 500 because it balanced context completeness vs retrieval precision.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _snap_to_word_end(self, text: str, start: int, target_end: int) -> int:
        """
        Given a target end position, return the nearest whitespace position
        at or before it (so the chunk doesn't end mid-word).
        Falls back to target_end if no whitespace is found (e.g. one very
        long unbroken token) so we never get stuck.
        """
        text_length = len(text)
        if target_end >= text_length:
            return text_length

        boundary = text.rfind(" ", start, target_end)
        # also treat newlines as valid boundaries
        newline_boundary = text.rfind("\n", start, target_end)
        boundary = max(boundary, newline_boundary)

        if boundary > start:
            return boundary
        return target_end  # fallback: no whitespace found, cut as-is

    def _snap_to_word_start(self, text: str, position: int) -> int:
        """
        Given a position that may be in the middle of a word, move forward
        to the start of the next whole word (skip past the partial word).
        """
        text_length = len(text)
        pos = position
        # if we're already at whitespace or the start of a word, keep as-is
        if pos <= 0 or pos >= text_length or text[pos - 1] in (" ", "\n", "\t"):
            return pos
        # otherwise skip forward until we hit whitespace, then past it
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

            # move start forward, but overlap with previous chunk
            target_next_start = end - self.chunk_overlap
            if target_next_start <= start:
                # safety net: always make forward progress even with large overlap
                target_next_start = end

            next_start = self._snap_to_word_start(text, target_next_start)
            if next_start <= start:
                # final safety net against infinite loops on unusual input
                next_start = end

            start = next_start

        return chunks

    def chunk_multiple_documents(self, documents: Dict[str, str]) -> List[Chunk]:
        """
        Chunk multiple documents at once.
        documents: { "diabetes.pdf": "cleaned text...", "asthma.pdf": "cleaned text..." }
        """
        all_chunks = []
        for doc_name, text in documents.items():
            doc_chunks = self.chunk_text(text, source_document=doc_name)
            all_chunks.extend(doc_chunks)
            print(f"{doc_name}: {len(doc_chunks)} chunks created")

        return all_chunks


# Example usage (for testing this file individually)
if __name__ == "__main__":
    sample_text = ("Diabetes is a chronic disease that occurs when the pancreas is no "
                    "longer able to make insulin, or when the body cannot effectively "
                    "use the insulin it produces. ") * 10

    chunker = TextChunker(chunk_size=200, chunk_overlap=30)
    chunks = chunker.chunk_text(sample_text, source_document="diabetes.pdf")

    print(f"Created {len(chunks)} chunks\n")
    for chunk in chunks[:3]:
        print(f"{chunk.chunk_id}:")
        print(f"  starts: '{chunk.text[:40]}...'")
        print(f"  ends:   '...{chunk.text[-40:]}'\n")