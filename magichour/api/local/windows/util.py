from collections import defaultdict
import math

from magichour.api.local.logging_util import get_logger, log_time

logger = get_logger(__name__)

@log_time
def extract_template_ids(windows):
    return [[timed_template.template_id for timed_template in window] for window in windows]

@log_time
def remove_junk_drawer(windows):
    return [[elem for elem in window if elem != -1] for window in windows]

@log_time
def uniqify_windows(windows):
    return [set(window) for window in windows]

def tf(elem, elems):
    return list(elems).count(elem) / len(elems)

def idf(elem, elemss):
    def num_containing():
        return sum(1 for elems in elemss if elem in elems)
    return math.log(len(elemss) / num_containing())

def tf_idf(elem, elems, elemss):
    return tf(elem, elems)*idf(elem, elemss)

# This is actually just an idf filter right now...
@log_time
def tf_idf_filter(elemss, threshold):
    new_elemss = []
    for elems in elemss:
        new_elems = []
        for elem in elems:
            score = idf(elem, elemss) # tf_idf(elem, elems, elemss)
            if score > threshold:
                new_elems.append(elem)
        new_elemss.append(new_elems)
    return new_elemss
