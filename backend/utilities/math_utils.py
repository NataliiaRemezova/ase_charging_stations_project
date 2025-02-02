import math
import random
from collections import Counter, OrderedDict


def intersection(set1, set2):
    """Returns the intersection of two sets."""
    return list(set(set1).intersection(set2))

def binomial_coefficient(n, k):
    """Computes the binomial coefficient (n choose k)."""
    return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

def generate_random_color():
    """Generates a random hexadecimal color code."""
    return "#" + "".join(random.choice('0123456789ABCDEF') for _ in range(6))

def count_frequencies(iterable):
    """Counts frequency of elements in an iterable and returns an ordered dictionary."""
    return OrderedDict(sorted(Counter(iterable).items()))