from __future__ import annotations

import os
import random
import re
from statistics import mean, median, multimode
from typing import Dict, List


Histogram = Dict[str, int]


def _read_source(source_text: str) -> str:
    """Return the raw text for `source_text`.

    `source_text` can be either:
    - a path to a text file, or
    - the text contents themselves.

    We first *try* to open it as a file; if that fails, we treat it as
    a literal string of text.
    """
    # If it's a real file path, read it
    if os.path.isfile(source_text):
        with open(source_text, "r", encoding="utf-8") as f:
            return f.read()

    # Otherwise, assume it's already the text contents
    return source_text


def _tokenize(text: str) -> list[str]:
    """Split raw text into a list of normalized word tokens.

    - Uses a simple regex to keep only word characters and apostrophes.
    - Lowercases everything so 'The' and 'the' count as the same word.
    """
    text = text.lower()
    # Find words (sequences of letters/digits/underscore/apostrophe)
    return re.findall(r"\b[\w']+\b", text)


def histogram(source_text: str) -> Histogram:
    """Build and return a word-frequency histogram from `source_text`.

    `source_text` can be either a filename or the contents of the file
    as a single string.
    """
    text = _read_source(source_text)
    words = _tokenize(text)

    hist: Histogram = {}
    for word in words:
        hist[word] = hist.get(word, 0) + 1
    return hist


def unique_words(hist: Histogram) -> int:
    """Return the number of distinct words in the histogram."""
    return len(hist)


def frequency(word: str, hist: Histogram) -> int:
    """Return how many times `word` appears according to `hist`.

    Returns 0 if the word does not occur.
    """
    return hist.get(word, 0)


def least_frequent_words(hist: Histogram) -> List[str]:
    """Return a list of the least frequent word(s) in the histogram."""
    if not hist:
        return []
    min_count = min(hist.values())
    return [word for word, count in hist.items() if count == min_count]


def most_frequent_words(hist: Histogram) -> List[str]:
    """Return a list of the most frequent word(s) in the histogram."""
    if not hist:
        return []
    max_count = max(hist.values())
    return [word for word, count in hist.items() if count == max_count]


def frequency_stats(hist: Histogram) -> Dict[str, object]:
    """Return basic statistics (mean, median, mode(s)) of word frequencies.

    The statistics are computed over the list of counts in the histogram.
    """
    if not hist:
        return {"mean": 0, "median": 0, "modes": []}
    counts = list(hist.values())
    return {
        "mean": mean(counts),
        "median": median(counts),
        "modes": multimode(counts),
    }


def sample_uniform(hist: Histogram) -> str:
    """Return a single random word from the histogram, ignoring frequency.

    Every distinct word has equal probability, regardless of its count.
    """
    if not hist:
        raise ValueError("Cannot sample from an empty histogram")
    return random.choice(list(hist.keys()))


def sample_weighted(hist: Histogram) -> str:
    """Return a random word from the histogram, weighted by frequency.

    A word that appears more times in the source text has proportionally
    higher probability of being selected.
    """
    if not hist:
        raise ValueError("Cannot sample from an empty histogram")

    total_tokens = sum(hist.values())
    dart = random.randint(1, total_tokens)
    fence = 0
    for word, count in hist.items():
        fence += count
        if fence >= dart:
            return word

    # Fallback; should not normally be reached
    return random.choice(list(hist.keys()))


if __name__ == "__main__":  # Simple manual test / demo
    import sys

    # If a filename or text is passed on the command line, use that;
    # otherwise fall back to the small example from the tutorial.
    if len(sys.argv) >= 2:
        source = sys.argv[1]
    else:
        source = "one fish two fish red fish blue fish"

    h = histogram(source)
    print("Histogram:", h)
    print("Unique words:", unique_words(h))
    for w in ("one", "fish", "mystery"):
        print(f"frequency({w!r}) =", frequency(w, h))
    print("Uniform sample:", sample_uniform(h))
    print("Weighted sample:", sample_weighted(h))
