from collections import defaultdict
import hdbscan

from pyspark.mllib.feature import Word2Vec

from magichour.api.local.util.namedtuples import Event
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


def event_gen_fp_growth(sc, log_lines,
                minSupport=0.2,
                numPartitions=10,
                windowLen=120,
                remove_junk_drawer=True):
    retval = list()
    windowed = windowRDD(sc, log_lines, windowLen, False)
    temp = FPGrowthRDD(windowed, minSupport, numPartitions).collect()

    items = [frozenset(fi.items) for fi in temp]
    pruned_items = list(get_longest_sets_possible(items))
    if remove_junk_drawer:
        for item_id, item in enumerate(pruned_items):
            event = Event(id=item_id, template_ids=[i for i in sorted(item, key=int) if i != -1])
            retval.append(event)
    else:
        for item_id, item in enumerate(pruned_items):
            event = Event(id=item_id, template_ids=[i for i in sorted(item, key=int)])
            retval.append(event)

    return retval

def event_gen_word2vec(sc, log_lines, window_size=60):
    D = log_lines.map(lambda logline: (int(logline.ts/window_size), (logline.ts, logline.templateId)))\
                .groupByKey()\
                .map(lambda (window,loglines): [str(templateId) for (ts,templateId) in sorted(loglines)])

    # Run Word2Vec
    model = Word2Vec().setVectorSize(16).setSeed(42).fit(D)
    model_vectors = model.getVectors()

    # mapping dict_distrib
    labels = []
    vectors = []
    for label, vector in model_vectors.items():
        labels.append(label)
        vectors.append(list(vector))

    # Clsutering
    output_events = defaultdict(list)
    for i, val in enumerate(hdbscan.HDBSCAN(min_cluster_size=2).fit_predict(vectors)):
        output_events[val].append(labels[i])

    # Create event objects
    events = []
    for item in output_events:
        event = Event(id=item, template_ids=map(int, output_events[item]))
        if len(event.template_ids) > 0:
            events.append(event)
    return events