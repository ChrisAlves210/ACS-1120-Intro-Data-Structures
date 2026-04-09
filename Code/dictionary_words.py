import random
import sys
from pathlib import Path


WORDS_FILE_PATH = "/usr/share/dict/words"


def load_words(path: str = WORDS_FILE_PATH):
    """Load words from the given file path, one word per line."""
    words_path = Path(path)
    if not words_path.is_file():
        raise FileNotFoundError(f"Words file not found at: {path}")

    with words_path.open("r", encoding="utf-8", errors="ignore") as f:
        # Strip whitespace and ignore empty lines
        return [line.strip() for line in f if line.strip()]


def random_sentence(num_words: int, words):
    """Return a sentence of num_words randomly chosen from words."""
    if num_words <= 0:
        return ""

    chosen = [random.choice(words) for _ in range(num_words)]
    sentence = " ".join(chosen)

    # Optionally end with a period if missing
    if not sentence.endswith((".", "!", "?")):
        sentence += "."
    return sentence


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 dictionary_words.py <num_words>")
        sys.exit(1)

    try:
        num = int(sys.argv[1])
    except ValueError:
        print("<num_words> must be an integer")
        sys.exit(1)

    try:
        all_words = load_words()
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    print(random_sentence(num, all_words))
