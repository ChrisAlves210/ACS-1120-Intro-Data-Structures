#!python

"""Benchmark count() performance across multiple histogram data structures.

This script compares four histogram implementations:
- List of tuples (flat associative array)
- Sorted list of tuples (binary search lookup)
- Dictionary (built-in dict)
- Hash table (custom HashTable with chaining)

For each implementation, we:
1) Build a histogram from unique words.
2) Analyze Big-O for count().
3) Benchmark count() many times on small and large histograms.
"""

from bisect import bisect_left
from statistics import mean
from timeit import Timer

from hashtable import HashTable


class ListTupleHistogram:
    """Histogram backed by an unsorted list of (word, count) tuples."""

    complexity = "count: O(n)"

    def __init__(self, words):
        self.entries = []
        for word in words:
            self.add_count(word)

    def add_count(self, word, count=1):
        for index, (entry_word, entry_count) in enumerate(self.entries):
            if entry_word == word:
                self.entries[index] = (entry_word, entry_count + count)
                return
        self.entries.append((word, count))

    def count(self, word):
        for entry_word, entry_count in self.entries:
            if entry_word == word:
                return entry_count
        return 0


class SortedListTupleHistogram:
    """Histogram backed by a sorted list of (word, count) tuples."""

    complexity = "count: O(log n)"

    def __init__(self, words):
        # Build from dict first, then sort once for predictable setup cost.
        counts = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
        self.entries = sorted(counts.items(), key=lambda pair: pair[0])
        self.keys = [entry_word for entry_word, _ in self.entries]

    def count(self, word):
        # Binary search over sorted entries by key.
        index = bisect_left(self.keys, word)
        if index < len(self.entries) and self.entries[index][0] == word:
            return self.entries[index][1]
        return 0


class DictHistogram:
    """Histogram backed by Python's built-in dict."""

    complexity = "count: O(1) average, O(n) worst"

    def __init__(self, words):
        self.data = {}
        for word in words:
            self.data[word] = self.data.get(word, 0) + 1

    def count(self, word):
        return self.data.get(word, 0)


class HashTableHistogram:
    """Histogram backed by the custom HashTable class."""

    complexity = "count: O(1) average, O(n) worst"

    def __init__(self, words):
        # More buckets reduces collisions for fairer average-case lookup.
        init_size = max(8, len(set(words)) * 2)
        self.table = HashTable(init_size)
        for word in words:
            if self.table.contains(word):
                self.table.set(word, self.table.get(word) + 1)
            else:
                self.table.set(word, 1)

    def count(self, word):
        try:
            return self.table.get(word)
        except KeyError:
            return 0


def make_unique_words(num_unique):
    """Create deterministic unique words for controlled benchmark sizes."""
    return ["word_{:05d}".format(index) for index in range(num_unique)]


def benchmark_count(histogram, search_word, iterations=5000, repeats=5):
    """Return timing stats for repeated count() calls."""
    timer = Timer(lambda: histogram.count(search_word))
    samples = [timer.timeit(number=iterations) for _ in range(repeats)]
    return {
        "iterations": iterations,
        "samples": samples,
        "best": min(samples),
        "avg": mean(samples),
    }


def print_analysis():
    """Print concise Big-O analysis for each count implementation."""
    print("Count() complexity analysis")
    print("- ListTupleHistogram: O(n) because lookup scans linearly")
    print("- SortedListTupleHistogram: O(log n) with binary search")
    print("- DictHistogram: O(1) average due to hash table indexing")
    print("- HashTableHistogram: O(1) average, O(n) worst under collisions")
    print()


def print_results_row(name, complexity, size, result):
    """Print one formatted benchmark row."""
    print(
        "{:<26} {:<31} {:>7} {:>10} {:>12.6f} {:>12.6f}".format(
            name,
            complexity,
            size,
            result["iterations"],
            result["best"],
            result["avg"],
        )
    )


def run_benchmarks():
    """Benchmark count() on small and large unique-word histograms."""
    sizes = [100, 10000]
    constructors = [
        ("ListTupleHistogram", ListTupleHistogram),
        ("SortedListTupleHistogram", SortedListTupleHistogram),
        ("DictHistogram", DictHistogram),
        ("HashTableHistogram", HashTableHistogram),
    ]

    print_analysis()
    print("Benchmark results (seconds)")
    print(
        "{:<26} {:<31} {:>7} {:>10} {:>12} {:>12}".format(
            "Structure",
            "Big-O",
            "Types",
            "Iterations",
            "Best",
            "Average",
        )
    )
    print("-" * 104)

    for size in sizes:
        words = make_unique_words(size)
        target = words[-1]  # Worst-case key for linear structures

        for name, constructor in constructors:
            histogram = constructor(words)
            # Keep total operations manageable on larger structures.
            iterations = 5000 if size == 100 else 1000
            result = benchmark_count(
                histogram,
                target,
                iterations=iterations,
                repeats=5,
            )
            print_results_row(
                name,
                constructor.complexity,
                size,
                result,
            )

    print("-" * 104)
    print("Tip: re-run a few times and compare trends, not a single raw number.")


if __name__ == "__main__":
    run_benchmarks()
