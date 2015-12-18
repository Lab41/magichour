import logging
import math
import numpy as np

logger = logging.getLogger(__name__)

def wss_gen(s, r):
    words = s.split()
    for result in ss_gen(words, r):
        yield result

def ss_gen(s, r):
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

def ss_dict(s, decay, ss_length, scheme):
    distances = {}
    ss_generator = ss_gen if scheme == "character" else wss_gen
    for ss, dist in ss_generator(s, ss_length):
        d = distances.get(ss, 0)
        if d == 0:
            d = math.pow(decay, dist)
        else:
            d += math.pow(decay, dist)
        distances[ss] = d
    return distances

def standardize_ss_dicts(ss_dicts):
    all_features = set()
    for ss_dict in ss_dicts:
        all_features = all_features | set(ss_dict.keys())
    all_features = list(all_features)
    ret = []
    for ss_dict in ss_dicts:
        ret.append(np.array([ss_dict.get(feature, 0) for feature in all_features]))
    return ret

def ssk(s1, s2, **kwargs):
    ss_len = kwargs.get("ss_len", 2)
    decay_factor = kwargs.get("decay_factor", 0.5)
    scheme = kwargs.get("scheme", "character")
    label_encoder = kwargs.get("label_encoder", None)

    if label_encoder:
        s1 = label_encoder.inverse_transform(s1.astype(int))[0]
        s2 = label_encoder.inverse_transform(s2.astype(int))[0]

    ss_dicts = [ss_dict(line, decay_factor, ss_len, scheme) for line in [s1, s2]]
    ss_dicts = standardize_ss_dicts(ss_dicts)

    # Normalize arrays
    norm1 = np.dot(ss_dicts[0], ss_dicts[0])
    norm2 = np.dot(ss_dicts[1], ss_dicts[1])
    norm = math.sqrt(norm1*norm2)

    ret =  np.dot(ss_dicts[0], ss_dicts[1])/norm
    return ret

def transform(lines, decay_factor, ss_len, scheme):
    ss_dicts = []
    for x in xrange(0, len(lines)):
        if x % (len(lines) / 10) == 0:
            logger.debug("%s percent processed..." % ((x*100)/len(lines)))
        line = lines[x]
        ss_dicts.append(ss_dict(line, decay_factor, ss_len, scheme))
    return standardize_ss_dicts(ss_dicts)

    #ss_dicts = [ss_dict(line, decay_factor, ss_len, scheme) for line in lines]
    #return standardize_ss_dicts(ss_dicts)
