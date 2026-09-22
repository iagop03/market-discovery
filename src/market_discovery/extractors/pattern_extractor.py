import re

from market_discovery.models import Niche

PATTERNS = [
    # [^.!?\n] (not [^.!?]) bounds a match to a single line: GitHub issue bodies in
    # particular are long, multi-line markdown with few sentence-ending periods, so
    # without excluding newlines these patterns matched clear across paragraphs and
    # captured meaningless multi-line fragments instead of one phrase.
    (r"i\s+need\s+([^.!?\n]+?)\s+but\s+(?:it\s+doesn't\s+exist|there's\s+no)", 1.0),
    (r"need\s+([^.!?\n]+?)\s+(?:but|and)", 0.8),
    (r"([^.!?\n]+?)\s+(?:is\s+)?(?:broken|terrible|awful|sucks|doesn't\s+work)", 0.7),
    (r"(?:looking\s+for|want|need)\s+(?:a\s+)?tool\s+(?:for|to)\s+([^.!?\n]+)", 0.8),
    (r"(?:alternative|replacement)\s+(?:for|to)\s+([^.!?\n]+)", 0.9),
    (r"([^.!?\n]+?)\s+as\s+a\s+service", 0.6),
]


class PatternExtractor:
    """Extracts candidate niches from raw text via regex patterns for common complaint/request phrasing."""

    def extract(self, text: str, source: str) -> list[Niche]:
        niches: list[Niche] = []
        text_lower = text.lower()

        for pattern, confidence in PATTERNS:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                title = match.group(1).strip()
                if 5 <= len(title) <= 200:
                    title = re.sub(r"\s+", " ", title)
                    niches.append(Niche(
                        title=title,
                        description=f"Mentioned on {source}",
                        source=source,
                        confidence=confidence,
                    ))
        return niches
