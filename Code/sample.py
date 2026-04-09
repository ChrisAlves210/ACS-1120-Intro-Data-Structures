from __future__ import annotations

import sys

from histogram import histogram, sample_uniform, sample_weighted


def build_hist_from_args(args: list[str]):
    """Build a histogram from command-line arguments.

    - If len(args) == 1, treat args[0] as a filename.
    - If len(args) > 1, treat args as the word list directly.
    """
    if not args:
        raise SystemExit(
            "Usage: python3 sample.py <word1> <word2> ... | python3 sample.py <filename>"
        )

    if len(args) == 1:
        # Single argument: assume it's a filename or raw text; histogram() handles both.
        source = args[0]
        return histogram(source)

    # Multiple arguments: treat them as the words directly.
    words_text = " ".join(args)
    return histogram(words_text)


def main(argv: list[str]) -> None:
    args = argv[1:]  # skip script name
    hist = build_hist_from_args(args)

    # Sample once uniformly and once with frequency weighting
    uniform_word = sample_uniform(hist)
    weighted_word = sample_weighted(hist)

    print("Uniform sample:", uniform_word)
    print("Weighted sample:", weighted_word)


if __name__ == "__main__":
    main(sys.argv)
