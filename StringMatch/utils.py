from __future__ import division
from math import floor, sqrt, log10

# Define our position aware cosine distance function
def cosine_sim(l1, l2, skip_count = 0):
    l1 = l1.split()
    l2 = l2.split()
    num_common = 0
    for i in range(skip_count, min(len(l1), len(l2))):
        if l1[i] == l2[i]:
            num_common +=1
    return num_common/sqrt((len(l1)-skip_count)*(len(l2)-skip_count))


def get_entropy_of_word_positions(word_counts, num_log_lines):
    # Calculate entropies for each word position
    entropies = []
    # Using nomeclature from section 3 (pg 232) of One Graph is Worth a Thousand Logs
    nc = num_log_lines
    for i in range(len(word_counts)):
        entropy = 0
        for (word, nkj) in word_counts[i].items():
            pkj = nkj / nc # This is floating pt division
            try:
                entropy += pkj * log10(pkj)
            except:
                print pkj, nkj, nc
                raise
        entropies.append(-1.0*entropy)
    return entropies