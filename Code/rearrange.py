import random
import sys


def rearrange_words(words):
    shuffled = words[:]
    random.shuffle(shuffled)
    return " ".join(shuffled)


if __name__ == "__main__":
    # sys.argv[0] is the script name, so skip it
    input_words = sys.argv[1:]
    if not input_words:
        print("Please provide one or more words as command-line arguments.")
    else:
        print(rearrange_words(input_words))
