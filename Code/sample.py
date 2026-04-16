from __future__ import annotations

import argparse
import sys
from collections import Counter
from collections.abc import Callable

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


def run_sampling_experiment(
    hist: dict[str, int],
    sampler: Callable[[dict[str, int]], str],
    trials: int,
) -> Counter[str]:
    """Sample from `hist` many times and return observed counts."""
    results: Counter[str] = Counter()
    for _ in range(trials):
        results[sampler(hist)] += 1
    return results


def print_probability_report(
    hist: dict[str, int],
    observed: Counter[str],
    trials: int,
    weighted: bool,
) -> None:
    """Print expected and observed probabilities for each word."""
    if weighted:
        total = sum(hist.values())
        expected = {word: count / total for word, count in hist.items()}
    else:
        p = 1 / len(hist)
        expected = {word: p for word in hist}

    print(f"Trials: {trials}")
    print("word\texpected\tobserved\tcount")
    for word in sorted(hist):
        expected_p = expected[word]
        observed_count = observed[word]
        observed_p = observed_count / trials
        print(f"{word}\t{expected_p:.4f}\t\t{observed_p:.4f}\t\t{observed_count}")


def parse_cli(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Parse known flags and keep remaining args as words/source."""
    parser = argparse.ArgumentParser(
        description="Sample words from a histogram.",
        add_help=True,
    )
    parser.add_argument(
        "--uniform",
        action="store_true",
        help="Sample uniformly from unique words (ignores frequencies).",
    )
    parser.add_argument(
        "--weighted",
        action="store_true",
        help="Sample weighted by word frequency (default behavior).",
    )
    parser.add_argument(
        "--test",
        type=int,
        default=0,
        metavar="N",
        help="Run N sampling trials and print observed vs expected probabilities.",
    )
    return parser.parse_known_args(argv[1:])


def main(argv: list[str]) -> None:
    options, args = parse_cli(argv)

    if options.uniform and options.weighted:
        raise SystemExit("Choose either --uniform or --weighted, not both.")

    hist = build_hist_from_args(args)
    sampler = sample_uniform if options.uniform else sample_weighted

    if options.test > 0:
        observed = run_sampling_experiment(hist, sampler, options.test)
        print_probability_report(
            hist,
            observed,
            options.test,
            weighted=(sampler is sample_weighted),
        )
        return

    print(sampler(hist))


if __name__ == "__main__":
    main(sys.argv)
