#!python

from __future__ import division, print_function  
import random


class Dictogram(dict):
    """Dictogram is a histogram implemented as a subclass of the dict type."""

    def __init__(self, word_list=None):
        """Initialize this histogram as a new dict and count given words."""
        super(Dictogram, self).__init__()  
        self.types = 0  
        self.tokens = 0  
        if word_list is not None:
            for word in word_list:
                self.add_count(word)

    def add_count(self, word, count=1):
        """Increase frequency count of given word by given count amount."""
        if word in self:
            self[word] += count
        else:
            # New word type
            self[word] = count
            self.types += 1
        self.tokens += count

    def frequency(self, word):
        """Return frequency count of given word, or 0 if word is not found."""
        return self.get(word, 0)

    def sample(self):
        """Return a word from this histogram, randomly sampled by weighting
        each word's probability of being chosen by its observed frequency."""
        dart = random.randint(1, self.tokens)
        fence = 0
        for word, count in self.items():
            fence += count
            if fence >= dart:
                return word

        return random.choice(list(self.keys()))


def print_histogram(word_list):
    print()
    print('Histogram:')
    print('word list: {}'.format(word_list))
    ##creates a dictogram and prints its contents##
    histogram = Dictogram(word_list)
    print('dictogram: {}'.format(histogram))
    print('{} tokens, {} types'.format(histogram.tokens, histogram.types))
    for word in word_list[-2:]:
        freq = histogram.frequency(word)
        print('{!r} occurs {} times'.format(word, freq))
    print()
    print_histogram_samples(histogram)


def print_histogram_samples(histogram):
    print('Histogram samples:')
    samples_list = [histogram.sample() for _ in range(10000)]
    samples_hist = Dictogram(samples_list)
    print('samples: {}'.format(samples_hist))
    print()
    print('Sampled frequency and error from observed frequency:')
    header = '| word type | observed freq | sampled freq  |  error  |'
    divider = '-' * len(header)
    print(divider)
    print(header)
    print(divider)
    green = '\033[32m'
    yellow = '\033[33m'
    red = '\033[31m'
    reset = '\033[m'
    for word, count in histogram.items():
        observed_freq = count / histogram.tokens
        samples = samples_hist.frequency(word)
        sampled_freq = samples / samples_hist.tokens
        error = (sampled_freq - observed_freq) / observed_freq
        color = green if abs(error) < 0.05 else yellow if abs(error) < 0.1 else red
        print('| {!r:<9} '.format(word)
            + '| {:>4} = {:>6.2%} '.format(count, observed_freq)
            + '| {:>4} = {:>6.2%} '.format(samples, sampled_freq)
            + '| {}{:>+7.2%}{} |'.format(color, error, reset))
    print(divider)
    print()


def main():
    import sys
    arguments = sys.argv[1:]  
    if len(arguments) >= 1:
        print_histogram(arguments)
    else:
        word = 'abracadabra'
        print_histogram(list(word))
        fish_text = 'one fish two fish red fish blue fish'
        print_histogram(fish_text.split())
        woodchuck_text = ('how much wood would a wood chuck chuck'
                          ' if a wood chuck could chuck wood')
        print_histogram(woodchuck_text.split())


if __name__ == '__main__':
    main()
