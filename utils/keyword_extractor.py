"""
utils/keyword_extractor.py
─────────────────────────
Option B: extract meaningful tags from a description WITHOUT an LLM.

Algorithm:
  1. Tokenise (lowercase, strip punctuation).
  2. Remove English stop-words (hard-coded compact list).
  3. Keep tokens that are 3+ characters and not purely numeric.
  4. Detect high-value tech bigrams (e.g. "machine learning") as compound tags.
  5. Return up to MAX_TAGS unique tags, ranked by frequency then length.
"""

from __future__ import annotations
import re
from collections import Counter
from typing import List

MAX_TAGS = 8

STOP_WORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "from",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "shall",
    "should",
    "may",
    "might",
    "must",
    "can",
    "could",
    "that",
    "this",
    "these",
    "those",
    "it",
    "its",
    "as",
    "up",
    "out",
    "so",
    "if",
    "then",
    "than",
    "not",
    "no",
    "nor",
    "into",
    "onto",
    "about",
    "like",
    "via",
    "per",
    "which",
    "who",
    "what",
    "when",
    "where",
    "how",
    "why",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "only",
    "own",
    "same",
    "too",
    "very",
    "just",
    "also",
    "well",
    "new",
    "use",
    "used",
    "using",
    "uses",
    "make",
    "makes",
    "made",
    "get",
    "gets",
    "set",
    "sets",
    "give",
    "given",
    "take",
    "taken",
    "able",
    "allow",
    "allows",
    "support",
    "supports",
    "provide",
    "provides",
    "based",
    "simple",
    "multiple",
    "single",
    "various",
    "different",
}

TECH_BIGRAMS = [
    "machine learning",
    "natural language",
    "computer vision",
    "deep learning",
    "large language",
    "language model",
    "neural network",
    "data pipeline",
    "real time",
    "real-time",
    "api gateway",
    "knowledge graph",
    "vector search",
    "semantic search",
    "image recognition",
    "speech recognition",
    "object detection",
    "data extraction",
    "document processing",
    "code generation",
    "text generation",
    "question answering",
    "sentiment analysis",
    "entity extraction",
    "named entity",
    "recommendation system",
    "anomaly detection",
    "time series",
    "data analysis",
    "data processing",
    "web scraping",
    "structured data",
    "unstructured data",
]


def extract_tags(text: str) -> List[str]:
    """Return a deduplicated, ranked list of keyword tags for *text*."""
    lower = text.lower()

    # 1. Detect compound bigram tags first
    compound_tags: List[str] = []
    for bigram in TECH_BIGRAMS:
        pattern = bigram.replace(" ", r"[\s\-]+")
        if re.search(pattern, lower):
            compound_tags.append(bigram.replace("-", " "))

    # 2. Tokenise: keep only alphabetic tokens 3+ chars
    tokens = re.findall(r"[a-z]{3,}", lower)

    # 3. Filter stop-words and count frequency
    filtered = [t for t in tokens if t not in STOP_WORDS]
    freq = Counter(filtered)

    # 4. Rank: frequency desc, then length desc (longer = more specific)
    ranked_singles = [
        word for word, _ in sorted(freq.items(), key=lambda x: (-x[1], -len(x[0])))
    ]

    # 5. Merge: compounds first, then singles, deduplicate
    seen: set[str] = set()
    tags: List[str] = []
    for tag in compound_tags:
        if tag not in seen:
            seen.add(tag)
            tags.append(tag)
    for word in ranked_singles:
        if word not in seen:
            seen.add(word)
            tags.append(word)
        if len(tags) >= MAX_TAGS:
            break

    return tags[:MAX_TAGS]
