import functools
import re
import multiprocessing
from collections import Counter

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


def count_templates(window):
    c = Counter()
    for timed_template in window.timed_templates:
        c[timed_template.template_id] += 1
    return c


def counter_issubset(counter1, counter2):
    return not counter1 - counter2


def apply_events_old(events, windows, mp=False):
    event_counters = {event.id : Counter(event.template_ids) for event in events}
    timed_events = []
    for window in windows:
        template_counts = count_templates(window)
        for event in events:
            num_occurrences = 0
            is_subset = True
            cur_counts = None
            while is_subset:
                if cur_counts:
                    is_subset = counter_issubset(event_counters[event.id], cur_counts)
                    cur_counts = cur_counts - event_counters[event.id]
                else:
                    is_subset = counter_issubset(event_counters[event.id], template_counts)
                    cur_counts = template_counts - event_counters[event.id]
                if is_subset:
                    num_occurrences += 1
            for occurrence in xrange(0, num_occurrences):
                timed_event = TimedEvent(window.start_time, window.end_time, event.id)
                timed_events.append(timed_event)
    return timed_events


#####

from collections import defaultdict


def count_templates(timed_templates):
    counts = defaultdict(int)
    for timed_template in timed_templates:
        counts[timed_template.template_id] += 1
    return counts


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


def calc_overlap(candidate_timed_template, orig_timed_template, logline_dict):
    candidate = logline_dict[candidate_timed_template.logline_id].replacements
    orig = logline_dict[orig_timed_template.logline_id].replacements
    """
    for k, v_list in orig.replacements.iteritems():
        orig_v_set = set(v_list)
        if k in candidate.replacements:
            cand_v_set = set(candidate.replacements[k])
            for cand_v in cand_v_set:
                if cand_v in orig_v_set:
                    overlap += len(cand_v) * weight_per_char
    return (jaccard_keys * key_weight) + (jaccard_vals * (1-key_weight))
    """
    return jaccard_dicts(candidate, orig) if candidate and orig else 0


"""
def search_window(idx, event, timed_templates, logline_dict, window_size):
    timed_template = timed_templates[idx]
    results = [timed_template]
    left_idx = idx-1
    right_idx = idx+1

    m = timed_template.ts % window_size
    start_time = timed_template.ts - m
    end_time = start_time + window_size

    search_set = set(event.template_ids)
    search_set.remove(timed_template.template_id)

    while search_set and (left_idx >= 0 or right_idx <= len(timed_templates)):
        candidates = defaultdict(list)
        if left_idx >= 0:
            l_timed_template = timed_templates[left_idx]
            if l_timed_template.ts >= start_time and l_timed_template.template_id in search_set:
                candidates[l_timed_template.template_id].append(l_timed_template)
                #results.append(l_timed_template)
                #search_set.remove(l_timed_template.template_id)
        if right_idx < len(timed_templates):
            r_timed_template = timed_templates[right_idx]
            if r_timed_template.ts <= end_time and r_timed_template.template_id in search_set:
                candidates[r_timed_template.template_id].append(r_timed_template)
                #results.append(r_timed_template)
                #search_set.remove(r_timed_template.template_id)

        for template_id, candidate_list in candidates.iteritems():
            if len(candidate_list) != 1:
                candidate_list = sorted(candidate_list, reverse=True, key=lambda candidate: calc_overlap(candidate, timed_template, logline_dict))
            winner = candidate_list[0]
            logger.info(": %s", calc_overlap(winner, timed_template, logline_dict))
            results.append(winner)
            search_set.remove(winner.template_id)

        left_idx -= 1
        right_idx += 1

    if search_set:
        return None

    return results
"""

def find_left_idx(idx, timed_templates, start_time):
    left_idx = 0
    for tt in reversed(timed_templates[:idx+1]):
        if tt.ts < start_time:
            break
        left_idx += 1
    return left_idx

def find_right_idx(idx, timed_templates, end_time):
    right_idx = 0
    for tt in timed_templates[idx:]:
        if tt.ts > end_time:
            break
        right_idx += 1
    return right_idx

def create_window(idx, timed_templates, window_size):
    timed_template = timed_templates[idx]
    start_time = timed_template.ts - (timed_template.ts % window_size)
    end_time = start_time + window_size
    left_idx = idx - find_left_idx(idx, timed_templates, start_time)
    right_idx = idx + find_right_idx(idx, timed_templates, end_time)
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
            relevant = sorted(relevant, reverse=True, key=lambda tt: calc_overlap(tt, timed_template, logline_dict))
            results[template_id] = relevant[0]
    return results.values()


# assume timed_templates are ordered
def apply_events(events, timed_templates, loglines, window_size=60, mp=False):
    template_counts = count_templates(timed_templates)
    logline_dict = {logline.id : logline for logline in loglines}
    timed_events = []
    for event in events:
        lct_id = get_least_common_template(template_counts, event.template_ids)
        for idx in xrange(0, len(timed_templates)):
            timed_template = timed_templates[idx]
            if timed_template.template_id == lct_id:
                results = search_window(idx, event, timed_templates, logline_dict, window_size)
                if results:
                    s = sorted(results, key=lambda result: result.ts)
                    timed_event = TimedEvent(event.id, timed_templates=s)
                    timed_events.append(timed_event)
    return timed_events