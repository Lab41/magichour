import os
import math

def ss_kernel(loglines, ss_len=2, decay_factor=0.5):
    """
    Implementation of String Subsequence Kernel (SSK) as described by Lodhi, Saunders, Shawe-Taylor, Cristianini, and Watkins in their paper
    Text Classificaiton Using String Kernels, published in Journal of Machine Learning Research 2 (2002).
    
    This implementation is a naive implementation that does not utilize the recursive computation for the SSK. It is meant to be used on small datasets.
    A recursive implementation using dynamic programming is available at: https://github.com/timshenkao/StringKernelSVM/blob/master/stringSVM.py

    Args:
        loglines: iterable containing each logline as a separate element
        ss_len: length of subsequence to tokenize on
        decay_factor: penalty to apply to larger distances (equivalent to lambda in the paper)

    Returns:
        feature_list: list of distinct subsequences identified in loglines, represents order of features returned in kernel
        kernel: list of lists containing the vectorized representation of loglines
    """
    temp = []
    all_features = set()
    for idx, logline in enumerate(loglines):
        distances = {}
        for ss, dist in ss_generator(logline, ss_len):
            d = distances.get(logline, 0)
            if d == 0:
                d = math.pow(decay_factor, dist)
            else:
                d *= math.pow(decay_factor, dist)
            distances[ss] = d
            all_features.add(ss)
        temp.append(distances)

    feature_list = []
    for feat in all_features:
        feature_list.append(feat)

    kernel = []
    for t in temp:
        vect = []
        for feat in feature_list:
            val = t.get(feat, 0)
            vect.append(val)
        kernel.append(vect)
    return (feature_list, kernel)

def ss_generator(s, r):
    """
    A generator for iterating through the subsequences (including non-contiguous substrings) of s. This code is based on: https://docs.python.org/2/library/itertools.html#itertools.combinations
    The primary difference is the addition of d as a return value, representing the subsequence length.

    Args:
        s: string to generate subsequences from
        r: length of subsequences to generate

    Returns:
        subsequence: the generated subsequence
        d: distance between first and last character of the subsequence (inclusive)
    """
    pool = tuple(s)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    d = indices[-1] - indices[0] + 1
    yield (tuple(pool[i] for i in indices), d)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        d = indices[-1] - indices[0] + 1
        yield (tuple(pool[i] for i in indices), d)
