import functools
import re
import multiprocessing
from collections import defaultdict

from magichour.api.local.util.log import get_logger
from magichour.api.local.util.namedtuples import TimedTemplate, TimedEvent

logger = get_logger(__name__)


def process_line(templates, logline):
    for template in templates:
        if template.match.match(logline.text):
            return TimedTemplate(logline.ts, template.id, logline.id)
    # -1 = did not match any template
    return TimedTemplate(logline.ts, -1, logline.id)


re_type = re.compile(r'type=(\S+)')
def process_auditd_line(templates, logline):
    audit_msg_type = re_type.search(logline.text)
    if not audit_msg_type:
        raise ValueError('Does not match expected auditd format; missing type=TYPE: %s'%logline.text)

    audit_msg_type = audit_msg_type.group(1)
    if audit_msg_type not in templates:
        raise KeyError("type=%s not in dictionary"%audit_msg_type)

    return TimedTemplate(logline.ts, templates[audit_msg_type], logline.id)


def apply_templates(templates, loglines, mp=True, type_template_auditd=False, **kwargs):
    """
    Applies the templates on an iterable. This function creates a list of TimedTemplate named tuples.
    In effect this will produce a list of which templates occurred at which times.
    -1 is the template_id that is used for a logline which was unable to be matched to a template.

    The templates accepted by this function is exactly the output of functions in template.py
    This function has the option of running in either multiprocessing mode (mp=True by default) or not.

    Args:
        templates: iterable Templates to apply
        loglines: loglines which will be examined

    Kwargs:
        mp: whether or not to run in multiprocessing mode (default: True)
        type_template_auditd: whether or not to use specialized auditd type template processing (default: False)

    Returns:
        timed_templates: a list of TimedTemplate named tuples that represent which templates occurred at which times in the log file.

    """
    # Change processing mode for auditd data by Templating based on type=TYPE
    if type_template_auditd:
        process_function = process_auditd_line
    else:
        process_function = process_line

    if mp:
        # Use multiprocessing.Pool to use multiple CPUs
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        f = functools.partial(process_function, templates)

        timed_templates = pool.map(func=f, iterable=loglines)
    else:
        # Do this the naive way with one CPU
        timed_templates = []
        for logline in loglines:
            timed_templates.append(process_function(templates, logline))
    return timed_templates


#####

def count_templates(timed_templates):
    counts = defaultdict(int)
    for timed_template in timed_templates:
        counts[timed_template.template_id] += 1
    return counts


### TODO: can delete get_least_common_template() if we switch to apply_events2()
def get_least_common_template(template_counts, template_ids):
    least_common_template = None
    for template_id in template_ids:
        if not least_common_template or template_counts[template_id] < template_counts[least_common_template]:
            least_common_template = template_id
    return least_common_template


def jaccard(s1, s2):
    return len(s1 & s2) / float(len(s1 | s2))


def get_inner_list_vals(d):
    d_vals = []
    for d_val_list in d.itervalues():
        for d_val in d_val_list:
            d_vals.append(d_val)
    return d_vals


def jaccard_dicts(d1, d2, key_weight=0.0):
    jaccard_keys = jaccard(d1.viewkeys(), d2.viewkeys())
    d1_vals = get_inner_list_vals(d1)
    d2_vals = get_inner_list_vals(d2)
    jaccard_vals = jaccard(frozenset(d1_vals), frozenset(d2_vals))
    return (jaccard_keys * key_weight) + (jaccard_vals * (1-key_weight))


def calc_similarity(candidate_timed_template, orig_timed_template, logline_dict):
    """
    Similarity between candidate and original: weighted Jaccard similarity between replacement keys and values
        1.0 = identical (best/greatest similarity)
        0.0 = nothing in common
    
    Returns: 0 <= similarity <= 1
    """
    candidate = logline_dict[candidate_timed_template.logline_id].replacements
    orig = logline_dict[orig_timed_template.logline_id].replacements
    return jaccard_dicts(candidate, orig) if candidate and orig else 0


def calc_proximity(candidate_timed_template, orig_timed_template):
    """
    Proximity between candidate and original: -abs(time difference) in seconds.
        0.0 = coincident (best/greatest proximity)
    
    Returns: proximity <= 0
    """
    return -abs(candidate_timed_template.ts - orig_timed_template.ts)


def calc_score(candidate_timed_template, orig_timed_template, logline_dict):
    """
    Compute score based on similarity and proximity.  
    Similarity is ranked first; equal similarities are then ranked by proximity.
    
    Returns: tuple(similarity, proximity)
    """
    return (calc_similarity(candidate_timed_template, orig_timed_template, logline_dict),
            calc_proximity(candidate_timed_template, orig_timed_template))


def find_left_idx(idx, timed_templates, start_time):
    """
    Return earliest index within window: [min(idx)].ts >= start_time
    """
    assert timed_templates[idx].ts >= start_time, 'starting index must be within window'
    while idx > 0 and timed_templates[idx-1].ts >= start_time:
        idx -= 1
    return idx

def find_right_idx(idx, timed_templates, end_time):
    """
    Return 1 + latest index within window: [max(idx-1)].ts <= end_time
    """
    assert timed_templates[idx].ts <= end_time, 'starting index must be within window'
    while idx < len(timed_templates) and timed_templates[idx].ts <= end_time:
        idx += 1
    return idx

def create_window(idx, timed_templates, window_size):
    timed_template = timed_templates[idx]
    start_time = timed_template.ts - window_size
    end_time = timed_template.ts + window_size
    left_idx = find_left_idx(idx, timed_templates, start_time)
    right_idx = find_right_idx(idx, timed_templates, end_time)
    return (left_idx, right_idx)

def search_window(idx, event, timed_templates, logline_dict, window_size):
    timed_template = timed_templates[idx]
    left_idx, right_idx = create_window(idx, timed_templates, window_size)
    window = timed_templates[left_idx:right_idx]
    results = {timed_template.template_id : timed_template}
    for template_id in event.template_ids:
        if template_id != timed_template.template_id:
            relevant = [tt for tt in window if tt.template_id == template_id]
            if not relevant:
                # We are missing one of the required template ID in this window
                return []
            relevant = sorted(relevant, reverse=True, key=lambda tt: calc_similarity(tt, timed_template, logline_dict))
            results[template_id] = relevant[0]
    return results.values()


# assume timed_templates are ordered
def apply_events(events, timed_templates, loglines, window_size=60, mp=False):
    template_counts = count_templates(timed_templates)
    logline_dict = {logline.id : logline for logline in loglines}

    # Create lookup table to speed up matching
    timed_template_dict = defaultdict(list)
    for idx, tt in enumerate(timed_templates):
        timed_template_dict[tt.template_id].append(idx)

    timed_events = []
    for event in events:
        lct_id = get_least_common_template(template_counts, event.template_ids)
        for idx in timed_template_dict[lct_id]:
            results = search_window(idx, event, timed_templates, logline_dict, window_size)
            if results:
                s = sorted(results, key=lambda result: result.ts)
                timed_event = TimedEvent(event.id, timed_templates=s)
                timed_events.append(timed_event)
    return timed_events


def search_window2(idx, ordered_event_template_ids, timed_templates, timed_template_dict, logline_dict, window_size):
    least_common_template = timed_templates[idx]
    left_idx, right_idx = create_window(idx, timed_templates, window_size)
    window = set(range(left_idx, right_idx))
    results = {least_common_template.template_id : least_common_template}
    # skip search for first/least_common_template_id since we know it is at idx
    for template_id in ordered_event_template_ids[1:]:
        # find all template_id within the window
        results[template_id] = [timed_templates[i] for i in window.intersection(timed_template_dict[template_id])]
        if not results[template_id]:
            # We are missing one of the required template ID in this window
            return []

    # Found all event templates
    # For each template that occurs multiple times, pick the one that scores best compared to the least_common_template
    for template_id in ordered_event_template_ids[1:]:
        relevant = sorted(results[template_id], reverse=True, key=lambda tt: calc_score(tt, least_common_template, logline_dict)) if len(results[template_id]) > 1 else results[template_id]
        results[template_id] = relevant[0]
    return results.values()


# assume timed_templates are ordered
def apply_events2(events, timed_templates, loglines, window_size=60, mp=False):
    template_counts = count_templates(timed_templates)
    logline_dict = {logline.id : logline for logline in loglines}

    # Create lookup table to speed up matching: set of all timed_template idx containing that template
    timed_template_dict = defaultdict(set)
    for idx, tt in enumerate(timed_templates):
        timed_template_dict[tt.template_id].add(idx)

    timed_events = []
    for event in events:
        # look for event template_ids in least-common to most-common order
        #   by looking in a window of timed_templates centered on each occurrence of the least-common template
        #     and stop processing the window as soon as we encounter a missing event template
        ordered_event_template_ids = sorted(event.template_ids, key=lambda template_id: template_counts[template_id])
        for idx in timed_template_dict[ordered_event_template_ids[0]]:
            results = search_window2(idx, ordered_event_template_ids, timed_templates, timed_template_dict, logline_dict, window_size)
            if results:
                s = sorted(results, key=lambda result: result.ts)
                timed_event = TimedEvent(event.id, timed_templates=s)
                timed_events.append(timed_event)
    return timed_events
