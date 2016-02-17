import uuid
from collections import defaultdict
from magichour.api.local.util.log import get_logger, log_time
from magichour.api.local.util.namedtuples import Event
from magichour.api.local.util.tfidf import tfidf_filter_namedtuple, tf_idf_filter

logger = get_logger(__name__)

######

@log_time
def remove_junk_drawer(windows):
    nojunk_windows = []
    for window in windows:
        template_ids = [template_id for template_id in window if template_id != -1]
        nojunk_windows.append(template_ids)
    return nojunk_windows

@log_time
def uniqify_windows(windows):
    return [list(set(window)) for window in windows]

######

# This function works on any named tuple with fields ["id", "template_ids"].

@log_time
def tf_idf_filter_window(windows, threshold):
    return tf_idf_filter(windows, threshold)

@log_time
def tfidf_filter_events(events, threshold, deduplicate=True):
    filtered_events = tfidf_filter_namedtuple(events, threshold, Event)
    if not deduplicate or not filtered_events:
        return filtered_events
    else:
        # Note that calling this will reassign random event IDs.
        logger.info("Removing subsets from tfidf_filter result...")
        template_id_sets = [frozenset(event.template_ids) for event in filtered_events]
        template_id_sets = get_nonsubsets(template_id_sets)
        filtered_events = [Event(id=str(uuid.uuid4()), template_ids=template_id_set) for template_id_set in template_id_sets]
        return filtered_events


######

def event_is_subset(not_subsets, candidate):
    for not_subset in not_subsets:
        if candidate.template_ids.issubset(not_subset.template_ids):
            return True
    return False


@log_time
def get_nonsubsets(input_sets, subset_eval_fn=None):
    def is_subset(not_subsets, candidate_set):
        for not_subset in not_subsets:
            if candidate_set.issubset(not_subset):
                return True
        return False

    if not subset_eval_fn:
        subset_eval_fn = is_subset

    input_dict = defaultdict(set)
    for i in input_sets:
        input_dict[len(i)].add(i)
    output_sets = set()
    lengths = sorted(input_dict.keys(), reverse=True) # Largest first
    for i in input_dict[lengths[0]]: # since they are all the longest length we know that they are good
        output_sets.add(i)
    for length in lengths[1:]:
        for item in input_dict[length]:
            if not subset_eval_fn(output_sets, item):
                output_sets.add(item)
    return output_sets