#!python
"""Text corpus cleaner / parser.

Each cleaning step is a small, named function that takes a string and returns
a cleaned string. `clean_text()` composes them in order.

Usage as a module:
    from cleanup import clean_text
    text = clean_text(raw_text)

Usage as a CLI script:
    python cleanup.py source.txt          # print cleaned text to stdout
    python cleanup.py source.txt > out.txt
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Individual cleaning steps
# ---------------------------------------------------------------------------

def decode_html_entities(text: str) -> str:
    """Convert HTML character entities to their Unicode equivalents.

    Handles both named (&amp;) and numeric (&#38; / &#x26;) forms so
    that corpus text collected via Diffbot or scraped HTML arrives clean.
    """
    return html.unescape(text)


def normalize_quotes(text: str) -> str:
    """Replace curly / typographic quote characters with plain ASCII equivalents.

    Curly single quotes  \u2018 \u2019  ->  '
    Curly double quotes  \u201c \u201d  ->  "
    Low-9 double quote   \u201e         ->  "
    Prime / backtick     \u2032 `       ->  '
    """
    replacements = {
        "\u2018": "'",   # left single quotation mark
        "\u2019": "'",   # right single quotation mark / apostrophe
        "\u201a": "'",   # single low-9 quotation mark
        "\u2032": "'",   # prime
        "`":      "'",
        "\u201c": '"',   # left double quotation mark
        "\u201d": '"',   # right double quotation mark
        "\u201e": '"',   # double low-9 quotation mark
        "\u2033": '"',   # double prime
    }
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    return text


def normalize_dashes(text: str) -> str:
    """Replace em-dashes and en-dashes with a plain hyphen surrounded by spaces."""
    text = re.sub(r"[\u2014\u2013]", " - ", text)  # em-dash, en-dash
    text = re.sub(r"--+", " - ", text)              # ASCII double/triple dashes
    return text


def remove_emphasis_markers(text: str) -> str:
    """Strip Markdown-style _ and * wrappers used for emphasis or bold.

    Examples:  _really_  ->  really
               *really*  ->  really
               **bold**  ->  bold
    """
    text = re.sub(r"\*{1,3}(\w[\w\s,.']*?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,2}(\w[\w\s,.']*?)_{1,2}", r"\1", text)
    return text


def remove_gutenberg_boilerplate(text: str) -> str:
    """Strip Project Gutenberg header and footer boilerplate.

    Everything before "*** START OF THE PROJECT GUTENBERG" and after
    "*** END OF THE PROJECT GUTENBERG" is considered boilerplate.
    """
    start_pattern = r"\*{3}\s*START OF.*?\*{3}"
    end_pattern   = r"\*{3}\s*END OF.*?\*{3}"

    match = re.search(start_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        text = text[match.end():]

    match = re.search(end_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        text = text[:match.start()]

    return text


def remove_section_symbols(text: str) -> str:
    """Remove miscellaneous non-prose symbols unlikely to appear in sentences."""
    symbols = "§†‡•‣⁂⁎⁑○●□■◦⦾⦿"
    for symbol in symbols:
        text = text.replace(symbol, " ")
    return text


def normalize_whitespace(text: str) -> str:
    """Collapse sequences of whitespace characters to a single space or newline.

    Preserves single blank lines (paragraph breaks) but collapses more than
    two consecutive newlines down to two.
    """
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces / tabs on a single line
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Composed pipeline
# ---------------------------------------------------------------------------

_PIPELINE = [
    decode_html_entities,
    normalize_quotes,
    normalize_dashes,
    remove_emphasis_markers,
    remove_gutenberg_boilerplate,
    remove_section_symbols,
    normalize_whitespace,
]


def clean_text(text: str) -> str:
    """Run all cleaning steps in order and return the cleaned text.

    Each step in _PIPELINE is applied sequentially so that it is trivial
    to add, remove, or reorder steps without touching any other logic.
    """
    for step in _PIPELINE:
        text = step(text)
    return text


def clean_file(path: str | Path) -> str:
    """Read a file, clean its text, and return the cleaned string."""
    raw = Path(path).read_text(encoding="utf-8", errors="ignore")
    return clean_text(raw)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python cleanup.py <source_file> [output_file]", file=sys.stderr)
        return 1

    source_path = Path(sys.argv[1])
    if not source_path.is_file():
        print(f"File not found: {source_path}", file=sys.stderr)
        return 1

    cleaned = clean_file(source_path)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
        output_path.write_text(cleaned, encoding="utf-8")
        word_count = len(cleaned.split())
        print(f"Saved cleaned corpus to {output_path} ({word_count} words)")
    else:
        print(cleaned)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
