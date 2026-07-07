"""
test_ingestion.py
Tests for Member 1's ingestion module (pdf_loader, text_cleaner, chunker)

Run with: pytest test_ingestion.py -v
"""

import pytest

# Fixed import locations matching your new flat root directory structure
from ingestion.text_cleaner import TextCleaner
from ingestion.chunker import TextChunker


class TestTextCleaner:

    def setup_method(self):
        self.cleaner = TextCleaner()

    def test_remove_extra_whitespace(self):
        text = "Hello    world\n\n\nThis is    a test"
        result = self.cleaner.remove_extra_whitespace(text)
        assert "    " not in result
        assert "\n\n\n" not in result

    def test_remove_page_numbers(self):
        text = "Diabetes symptoms\n12\nInclude fatigue"
        result = self.cleaner.remove_page_numbers(text)
        assert "12" not in result.split('\n')

    def test_remove_headers_footers(self):
        text = "WHO Fact Sheet\nDiabetes is a chronic disease"
        result = self.cleaner.remove_headers_footers(text, known_headers=["WHO Fact Sheet"])
        assert "WHO Fact Sheet" not in result
        assert "Diabetes is a chronic disease" in result

    def test_medical_notation_preservation(self):
        """
        CRITICAL VIVA TEST: Ensures vital clinical dosage limits, ranges,
        and measurement safety symbols are never stripped or corrupted.
        """
        medical_text = "Dosage: 40-120 mg, Temp: 38.5°C, Value: ≥ 5.0 μg ± 0.2"
        result = self.cleaner.remove_special_characters(medical_text)
        
        # Verify clinical measurements survive completely intact
        assert "40-120" in result, "Safety Failure: Dosage range hyphen broken!"
        assert "38.5°C" in result, "Safety Failure: Temperature degree symbol stripped!"
        assert "≥" in result, "Safety Failure: Laboratory upper bound comparison symbol stripped!"
        assert "μg" in result, "Safety Failure: Microgram dose notation symbol corrupted!"
        assert "±" in result, "Safety Failure: Measurement tolerance interval variation indicator lost!"

    def test_full_clean_pipeline(self):
        text = "WHO Fact Sheet\n\n\nDiabetes   is chronic.\n12"
        result = self.cleaner.clean(text, known_headers=["WHO Fact Sheet"])
        assert "WHO Fact Sheet" not in result
        assert "Diabetes" in result


class TestTextChunker:

    def setup_method(self):
        self.chunker = TextChunker(chunk_size=100, chunk_overlap=20)

    def test_chunk_creates_multiple_chunks(self):
        long_text = "Diabetes is a chronic disease. " * 20  # long enough to need multiple chunks
        chunks = self.chunker.chunk_text(long_text, source_document="diabetes.pdf")
        assert len(chunks) > 1

    def test_chunk_has_correct_source(self):
        text = "Sample disease information text."
        chunks = self.chunker.chunk_text(text, source_document="test.pdf")
        for chunk in chunks:
            assert chunk.source_document == "test.pdf"

    def test_chunk_ids_are_unique(self):
        text = "Diabetes symptoms include fatigue and thirst. " * 10
        chunks = self.chunker.chunk_text(text, source_document="diabetes.pdf")
        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))  # no duplicates

    def test_short_text_produces_one_chunk(self):
        short_text = "Short text."
        chunks = self.chunker.chunk_text(short_text, source_document="test.pdf")
        assert len(chunks) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])