#!python
"""Markov chain sentence generator.

Usage:
    python markov.py [corpus_file] [num_words]

Examples:
    python markov.py data/corpus.txt 15
    python markov.py "one fish two fish red fish blue fish" 10
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

from dictogram import Dictogram


# ---------------------------------------------------------------------------
# Tokenisation (shared with histogram.py but kept local to avoid coupling)
# ---------------------------------------------------------------------------

def _read_source(source: str) -> str:
    """Return raw text from a file path or a literal string."""
    p = Path(source)
    if p.is_file():
        return p.read_text(encoding="utf-8", errors="ignore")
    return source


def _tokenize(text: str) -> list[str]:
    """Split text into lowercased word tokens."""
    return re.findall(r"\b[\w']+\b", text.lower())


# ---------------------------------------------------------------------------
# Building the Markov chain
# ---------------------------------------------------------------------------

MarkovChain = dict[str, Dictogram]


def build_markov_chain(source: str, order: int = 1) -> MarkovChain:
    """Learn a Markov chain from *source* (file path or raw text).

    Returns a dict mapping each token (state) to a Dictogram of the tokens
    that follow it.  *order* is kept at 1 (bigram model) for now.
    """
    text = _read_source(source)
    tokens = _tokenize(text)

    chain: MarkovChain = {}
    for i in range(len(tokens) - order):
        state = tokens[i]
        next_token = tokens[i + order]
        if state not in chain:
            chain[state] = Dictogram()
        chain[state].add_count(next_token)

    return chain


# ---------------------------------------------------------------------------
# Random walk / sentence generation
# ---------------------------------------------------------------------------

def _random_start(chain: MarkovChain) -> str:
    """Pick a starting word.

    Prefer words that could plausibly start a sentence (i.e. words that
    follow sentence-ending punctuation in the corpus, or just a random word
    when no such preference is available).
    """
    return random.choice(list(chain.keys()))


def generate_sentence(chain: MarkovChain, num_words: int = 15, start: str | None = None) -> str:
    """Walk the Markov chain and return a sentence of *num_words* words.

    If the walk gets stuck (reaches a state with no outgoing transitions),
    it restarts from a new random state so it can always produce *num_words*
    words.
    """
    if not chain:
        raise ValueError("Markov chain is empty")

    word = start if (start and start in chain) else _random_start(chain)
    words: list[str] = [word]

    for _ in range(num_words - 1):
        if word in chain:
            word = chain[word].sample()
        else:
            # Stuck (terminal state) — restart from a random state
            word = _random_start(chain)
        words.append(word)

    sentence = " ".join(words)
    # Capitalise first letter and add a period if needed
    sentence = sentence[0].upper() + sentence[1:]
    if not sentence[-1] in ".!?":
        sentence += "."
    return sentence


# ---------------------------------------------------------------------------
# Script entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]

    # Determine source and word count from CLI args
    if len(args) >= 1:
        source = args[0]
    else:
        source = "data/corpus.txt"

    num_words = 15
    if len(args) >= 2:
        try:
            num_words = int(args[1])
        except ValueError:
            pass

    print("Building Markov chain …", file=sys.stderr)
    chain = build_markov_chain(source)
    print(f"Chain has {len(chain)} states.", file=sys.stderr)

    for _ in range(5):
        print(generate_sentence(chain, num_words))
