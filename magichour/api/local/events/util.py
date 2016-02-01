from collections import defaultdict
from magichour.api.local.logging_util import get_logger, log_time

logger = get_logger(__name__)

@log_time
def get_longest_sets_possible(input_sets):
    def is_subset(main_set, item):
        is_subset = False
        for main_item in main_set:
            if item.issubset(main_item):
                is_subset = True
        return is_subset
        
    input_dict = defaultdict(set)
    for i in input_sets:
        input_dict[len(i)].add(i)
    output_sets = set()
    lengths = sorted(input_dict.keys(), reverse=True) # Largest first
    for i in input_dict[lengths[0]]: # since they are all the longest length we know that they are good
        output_sets.add(i) 
    for length in lengths[1:]:
        for item in input_dict[length]:
            if not is_subset(output_sets, item):
                output_sets.add(item)
    return output_sets
