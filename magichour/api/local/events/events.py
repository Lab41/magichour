from fp_growth import find_frequent_itemsets
from magichour.lib.PARIS import paris

# both algorithms accept list of iterables representing transactional windows

def paris(windows, r_slack):
    A, R = paris.PARIS(windows, r_slack)
    # return itemsets

def fp_growth(windows, min_support):
    itemsets = []
    for itemset in find_frequent_itemsets(windows, min_support):
        itemsets.append(itemset)
    return itemsets
