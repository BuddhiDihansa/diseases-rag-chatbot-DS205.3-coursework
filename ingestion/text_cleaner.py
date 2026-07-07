"""
text_cleaner.py
Member 1 - Data Engineering

Purpose: Clean raw extracted PDF text before chunking
(remove headers, footers, page numbers, extra whitespace, etc.)

FIXED VERSION: remove_special_characters() previously stripped the
hyphen character in some contexts inconsistently and dropped medical
notation symbols (°, ≥, ≤, ±, μ) entirely. This silently corrupted
dosage ranges - e.g. "40-120 mg" became "40120 mg", which is a real
patient-safety risk since it looks like a single dose instead of a
range. This version explicitly whitelists the hyphen and common
medical symbols so dosage ranges and clinical notation survive intact.
"""

import re


class TextCleaner:
    """
    Cleans raw text extracted from PDFs.
    Each cleaning step is a separate method so it's easy to test
    and easy to explain individually during the Viva.
    """

    def __init__(self):
        pass

    def remove_extra_whitespace(self, text: str) -> str:
        """Collapse multiple spaces/newlines into single ones."""
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def remove_page_numbers(self, text: str) -> str:
        """Remove standalone page numbers (e.g., lines that are just '12')."""
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if not line.strip().isdigit()]
        return '\n'.join(cleaned_lines)

    def remove_special_characters(self, text: str) -> str:
        """
        Remove unwanted symbols but keep normal punctuation AND
        medical/clinical notation that matters for dosage accuracy:
        - hyphen (-)      : dosage ranges, e.g. "40-120 mg"
        - degree (°)      : temperature, e.g. "38.5°C"
        - >= / <= (≥ ≤)   : lab value comparators
        - plus-minus (±)  : measurement tolerances
        - micro (μ)       : microgram dosages, e.g. "50 μg"
        """
        text = re.sub(r'[^\w\s.,;:!?()\-\'\"%/°≥≤±μ]', '', text)
        return text

    def remove_headers_footers(self, text: str, known_headers: list = None) -> str:
        """
        Remove repeated headers/footers if you know what they look like.
        Example: known_headers = ["WHO Fact Sheet", "Page"]
        """
        if not known_headers:
            return text

        lines = text.split('\n')
        cleaned_lines = [
            line for line in lines
            if not any(header.lower() in line.lower() for header in known_headers)
        ]
        return '\n'.join(cleaned_lines)

    def clean(self, text: str, known_headers: list = None) -> str:
        """Run the full cleaning pipeline in order."""
        text = self.remove_headers_footers(text, known_headers)
        text = self.remove_page_numbers(text)
        text = self.remove_special_characters(text)
        text = self.remove_extra_whitespace(text)
        return text


# Example usage (for testing this file individually)
if __name__ == "__main__":
    sample_text = """
    WHO Fact Sheet
    Diabetes    is a chronic disease...
    Tab. propranolol 40-120 mg BD, temperature >= 38.5 C

    12
    It occurs when the pancreas...
    """

    cleaner = TextCleaner()
    cleaned = cleaner.clean(sample_text, known_headers=["WHO Fact Sheet"])
    print(cleaned)
