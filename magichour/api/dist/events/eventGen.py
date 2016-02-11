from collections import defaultdict
from magichour.api.dist.window.window import windowRDD
from magichour.api.dist.FPGrowth.FPGrowth import FPGrowthRDD


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
    # Largest First
    lengths = sorted(input_dict.keys(), reverse=True)

    # since they are all the longest length we know that they are good
    for i in input_dict[lengths[0]]:
        output_sets.add(i)

    for length in lengths[1:]:
        for item in input_dict[length]:
            if not is_subset(output_sets, item):
                output_sets.add(item)
    return output_sets


def eventGenRDD(sc, transactions,
                minSupport=0.2,
                numPartitions=10,
                windowLen=120,
                remove_junk_drawer=True):
    retval = list()
    windowed = windowRDD(sc, transactions, windowLen, False)
    temp = FPGrowthRDD(windowed, minSupport, numPartitions).collect()

    items = [frozenset(fi.items) for fi in temp]
    pruned_items = list(get_longest_sets_possible(items))
    if remove_junk_drawer:
        for item in pruned_items:
            line = ' '.join([str(i) for i in sorted(item, key=int) if i != -1])
            retval.append(line)
    else:
        for item in pruned_items:
            line = ' '.join([str(i) for i in sorted(item, key=int)])
            retval.append(line)

    return retval
