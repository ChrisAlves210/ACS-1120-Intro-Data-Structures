#!python
"""Markov chain sentence generator.

Usage:
    python markov.py [corpus_file] [num_words] [order]

Examples:
    python markov.py data/corpus.txt 15 1
    python markov.py "one fish two fish red fish blue fish" 10 2
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

from dictogram import Dictogram
from linked_queue import Queue


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

MarkovState = tuple[str, ...]
MarkovChain = dict[MarkovState, Dictogram]


def build_markov_chain(source: str, order: int = 1) -> MarkovChain:
    """Learn a Markov chain from *source* (file path or raw text).

    Returns a dict mapping each state (an n-tuple of tokens) to a Dictogram
    of the tokens that follow it.
    """
    if order < 1:
        raise ValueError("order must be at least 1")

    text = _read_source(source)
    tokens = _tokenize(text)
    if len(tokens) <= order:
        return {}

    chain: MarkovChain = {}

    # Sliding context window of previous n tokens.
    window = Queue(tokens[:order])
    for i in range(order, len(tokens)):
        state = tuple(window)
        next_token = tokens[i]
        if state not in chain:
            chain[state] = Dictogram()
        chain[state].add_count(next_token)

        window.dequeue()
        window.enqueue(next_token)

    return chain


# ---------------------------------------------------------------------------
# Random walk / sentence generation
# ---------------------------------------------------------------------------

def _random_start(chain: MarkovChain) -> MarkovState:
    """Pick a random starting state from learned states."""
    return random.choice(list(chain.keys()))


def _chain_order(chain: MarkovChain) -> int:
    """Infer model order from any existing state key."""
    return len(next(iter(chain)))


def generate_sentence(
    chain: MarkovChain,
    num_words: int = 15,
    start: str | MarkovState | None = None,
) -> str:
    """Walk the Markov chain and return a sentence of *num_words* words.

    If the walk gets stuck (reaches a state with no outgoing transitions),
    it restarts from a new random state so it can always produce *num_words*
    words.
    """
    if not chain:
        raise ValueError("Markov chain is empty")
    if num_words <= 0:
        return ""

    order = _chain_order(chain)

    if isinstance(start, tuple) and len(start) == order and start in chain:
        state = start
    elif isinstance(start, str) and order == 1 and (start,) in chain:
        state = (start,)
    else:
        state = _random_start(chain)

    words: list[str] = list(state)
    if len(words) > num_words:
        words = words[:num_words]

    window = Queue(state)

    while len(words) < num_words:
        current_state = tuple(window)
        if current_state in chain:
            next_word = chain[current_state].sample()
            if len(window) == order:
                window.dequeue()
            window.enqueue(next_word)
            words.append(next_word)
        else:
            # Stuck (terminal state) — restart from a random state
            restart_state = _random_start(chain)
            window = Queue(restart_state)
            words.append(restart_state[-1])

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
    order = 1
    if len(args) >= 2:
        try:
            num_words = int(args[1])
        except ValueError:
            pass
    if len(args) >= 3:
        try:
            order = int(args[2])
        except ValueError:
            pass

    print(f"Building order-{order} Markov chain ...", file=sys.stderr)
    chain = build_markov_chain(source, order=order)
    print(f"Chain has {len(chain)} states.", file=sys.stderr)

    for _ in range(5):
        print(generate_sentence(chain, num_words))
