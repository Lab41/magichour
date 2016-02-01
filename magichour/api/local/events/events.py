from collections import defaultdict
import math

from fp_growth import find_frequent_itemsets
from magichour.lib.PARIS import paris
from magichour.api.local.logging_util import get_logger

logger = get_logger(__name__)

# both algorithms accept list of iterables of TimedTemplates representing transactional windows

def paris(windows, r_slack):
    A, R = paris.PARIS(windows, r_slack)
    # return itemsets

def fp_growth(windows, min_support, iterations=0): 
    itemsets = []
    
    if 0 < min_support < 1:
        new_support = math.ceil(min_support * len(windows))
        logger.info("Min support %s%% of %s: %s", min_support*100, len(windows), new_support)
        min_support = new_support
    
    itemset_gen = find_frequent_itemsets(windows, min_support)
    if iterations > 1:
        for x in xrange(0, iterations):
            itemsets.append(frozenset(next(itemset_gen)))
    else:
        for itemset in itemset_gen:
            itemsets.append(frozenset(itemset))
    return itemsets #list(get_longest_sets_possible(itemsets))