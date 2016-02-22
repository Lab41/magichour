import math

from collections import Counter
from magichour.api.local.util.log import log_time, get_logger
from magichour.api.local.util.namedtuples import Event

logger = get_logger(__name__)


def tf(elem, elems):
    return list(elems).count(elem) / len(elems)


def idf(elem, elemss):
    def num_containing():
        return sum(1 for elems in elemss if elem in elems)
    return math.log(len(elemss) / num_containing())


def idf_simple(num_windows_containing_element, total_windows):
    return math.log(total_windows / num_windows_containing_element)


def tf_idf(elem, elems, elemss):
    return tf(elem, elems) * idf(elem, elemss)


def tf_idf_filter(elemss, threshold):
    global_counts_tf = Counter()
    global_counts_idf = Counter()
    for items in elemss:
        global_counts_tf.update(items)
        for item in set(items):
            global_counts_idf[item] += 1
        # global_counts_tf.update(items.keys())

    to_filter = set()
    for elem in global_counts_idf:
        score = idf_simple(global_counts_idf[elem], len(elemss))
        if score <= threshold:
            to_filter.add(elem)
    return to_filter

    # new_elemss = []
    # for elems in elemss:
    #     new_elems = []
    #     for elem in elems:
    #         score = idf_simple(elem, global_counts_tf, len(elemss)) # tf_idf(elem, elems, elemss)
    #         if score >= threshold:
    #             for i in range(elems[elem]):
    #                 new_elems.append(elem)
    #     new_elemss.append(new_elems)
    # return new_elemss

"""
@log_time
def tfidf_filter_namedtuple(ntuples, threshold):
    #template_ids = [Counter([template_id for template_id in ntuple.template_ids]) for ntuple in ntuples]
    template_ids = [[template_id for template_id in event.template_ids] for event in ntuples]
    templates_to_filter = tf_idf_filter(template_ids, threshold)
    try:
        ret = []
        for ntuple in ntuples:
            template_ids =[]
            for template_id in ntuple.template_ids:
                if template_id not in templates_to_filter:
                    template_ids.append(template_id)
            ret.append(ntuple_type(ntuple.id, template_ids))
    except AttributeError as ae:
        ret = [ntuple_type([template_id for template_id in ntuple.template_ids if
                            template_id not in templates_to_filter]) for ntuple in ntuples]
        #ret = [ntuple_type(filtered_ids) for filtered_ids in filtered if filtered_ids]
    return ret
"""


@log_time
def tfidf_filter_event_defs(events, threshold):
    template_ids = [[template_id for template_id in event.template_ids]
                    for event in events]
    to_filter = tf_idf_filter(template_ids, threshold)
    filtered_events = []
    for event in events:
        template_ids = []
        for template_id in event.template_ids:
            if template_id not in to_filter:
                template_ids.append(template_id)
        e = Event(id=event.id, template_ids=template_ids)
        filtered_events.append(e)
    return filtered_events
