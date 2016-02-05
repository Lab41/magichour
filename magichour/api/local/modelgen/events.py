import math
import uuid

from fp_growth import find_frequent_itemsets

from magichour.api.local.util.log import get_logger
from magichour.api.local.util.modelgen import get_nonsubsets
from magichour.api.local.util.namedtuples import Event

from magichour.lib.PARIS import paris as paris_lib

logger = get_logger(__name__)

# windows = list of Window named tuples
# return list of Event named tuples

def paris(windows, r_slack, num_iterations):
    ws = [set([template_id for template_id in w.template_ids]) for w in windows]
    A, R = paris_lib.PARIS(ws, r_slack, num_iterations=num_iterations)

    itemsets = [frozenset(a) for a in A]
    ret = [Event(id=str(uuid.uuid4()), template_ids=template_ids) for template_ids in itemsets]
    return ret

def fp_growth(windows, min_support, iterations=0): 
    itemsets = []
    
    if 0 < min_support < 1:
        new_support = math.ceil(min_support * len(windows))
        logger.info("Min support %s%% of %s: %s", min_support*100, len(windows), new_support)
        min_support = new_support

    ws = [[template_id for template_id in w.template_ids] for w in windows]
    itemset_gen = find_frequent_itemsets(ws, min_support)
    if iterations > 1:
        for x in xrange(0, iterations):
            template_ids = frozenset(next(itemset_gen))
            itemsets.append(template_ids)
    else:
        for itemset in itemset_gen:
            template_ids = frozenset(itemset)
            itemsets.append(template_ids)

    logger.info("Removing subsets from fp_growth output...")
    itemsets = get_nonsubsets(itemsets)

    ret = [Event(id=str(uuid.uuid4()), template_ids=template_ids) for template_ids in itemsets]
    return ret
