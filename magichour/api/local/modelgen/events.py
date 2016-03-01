import math
import uuid
from collections import defaultdict

from magichour.api.local.util.log import get_logger
from magichour.api.local.util.modelgen import get_nonsubsets
from magichour.api.local.util.namedtuples import Event

from magichour.lib.PARIS import paris as paris_lib

logger = get_logger(__name__)

# windows = list of Window named tuples
# return list of Event named tuples


def paris(windows, r_slack, num_iterations, tau=1.0):
    ws = [set([template_id for template_id in w]) for w in windows]
    A, R = paris_lib.PARIS(ws, r_slack, num_iterations=num_iterations, tau=tau)

    itemsets = [frozenset(a) for a in A]
    ret = [Event(id=str(uuid.uuid4()), template_ids=template_ids)
           for template_ids in itemsets]
    return ret


def glove(windows, num_components=16, glove_window=10, epochs=20):
    import glove
    import hdbscan
    import multiprocessing

    ws = [[template_id for template_id in w] for w in windows]
    corpus = glove.Corpus()
    corpus.fit(ws, window=glove_window)
    # TODO: Explore reasonable glove defaults
    glove_model = glove.Glove(no_components=num_components, learning_rate=0.05)
    glove_model.fit(
        corpus.matrix,
        epochs=epochs,
        no_threads=multiprocessing.cpu_count(),
        verbose=False)
    glove_model.add_dictionary(corpus.dictionary)

    labels = []
    vectors = []
    # TODO: Explore how to pull data more nicely from glove
    for key in glove_model.__dict__['dictionary']:
        word_vector_index = glove_model.__dict__['dictionary'][key]
        labels.append(key)
        vectors.append(
            list(
                glove_model.__dict__['word_vectors'][word_vector_index]))

    # Clustering
    output_events = defaultdict(list)
    for i, val in enumerate(hdbscan.HDBSCAN(
            min_cluster_size=2).fit_predict(vectors)):
        output_events[val].append(labels[i])

    # Create event objects
    events = []
    for item in output_events:
        event = Event(
            id=str(
                uuid.uuid4()), template_ids=map(
                int, output_events[item]))
        if len(event.template_ids) > 0:
            events.append(event)
    return events


def fp_growth(windows, min_support, iterations=0):
    from fp_growth import find_frequent_itemsets
    itemsets = []

    if 0 < min_support < 1:
        new_support = math.ceil(min_support * len(windows))
        logger.info(
            "Min support %s%% of %s: %s",
            min_support * 100,
            len(windows),
            new_support)
        min_support = new_support

    itemset_gen = find_frequent_itemsets(windows, min_support)
    if iterations > 1:
        for x in xrange(0, iterations):
            template_ids = frozenset(next(itemset_gen))
            itemsets.append(template_ids)
    else:
        for itemset in itemset_gen:
            template_ids = frozenset(itemset)
            itemsets.append(template_ids)

    logger.info("Removing subsets from fp_growth output...")
    if len(itemsets):
        itemsets = get_nonsubsets(itemsets)

    ret = [Event(id=str(uuid.uuid4()), template_ids=template_ids)
           for template_ids in itemsets]
    return ret
