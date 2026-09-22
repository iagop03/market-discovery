import html
import re

from market_discovery.models import Niche

# A genuine product/niche name is a short phrase, not a clause. Long-form prose (GitHub
# issue bodies especially) often runs many words before the next line break or sentence
# punctuation, so without a tight upper bound the captured group ends up being a whole
# rambling clause instead of a plausible niche name.
MAX_TITLE_LENGTH = 80

# A real niche name reads as a noun phrase ("cobol to python translator", "the ci
# pipeline") — articles like "a"/"the" leading into one are fine. These words instead
# mark a capture that starts mid-clause (a pronoun, conjunction, preposition, or linking
# verb with nothing but trailing context after it), which is never a plausible niche name.
LEADING_STOPWORDS = {
    "to", "it", "that", "this", "these", "those", "is", "are", "was", "were",
    "there", "which", "who", "i", "we", "you", "he", "she", "they",
    "and", "or", "but", "if", "as", "of", "in", "on", "at", "for", "with",
}

HTML_TAG = re.compile(r"<[^>]+>")

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
        # StackOverflow's `withbody` filter (and GitHub markdown, more loosely) can carry
        # HTML entities (&#x27;, &quot;, ...) straight into the text; decode before matching
        # so they don't end up embedded in captured titles.
        text_lower = html.unescape(text).lower()

        for pattern, confidence in PATTERNS:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE | re.MULTILINE):
                title = match.group(1).strip()
                if not (5 <= len(title) <= MAX_TITLE_LENGTH):
                    continue
                if HTML_TAG.search(title):
                    continue
                first_word = re.match(r"[a-z']+", title)
                if first_word and first_word.group(0) in LEADING_STOPWORDS:
                    continue

                title = re.sub(r"\s+", " ", title)
                niches.append(Niche(
                    title=title,
                    description=f"Mentioned on {source}",
                    source=source,
                    confidence=confidence,
                ))
        return niches
