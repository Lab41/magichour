import functools
import multiprocessing
from collections import Counter

from magichour.api.local.util.log import get_logger
from magichour.api.local.util.namedtuples import TimedTemplate, TimedEvent, ModelEvalWindow

logger = get_logger(__name__)

def process_line(templates, logline):
    for template in templates:
        if template.match.match(logline.text):
            return TimedTemplate(logline.ts, template.id)
    # -1 = did not match any template
    return TimedTemplate(logline.ts, -1)

def process_auditd_line(templates, logline):
    first_key_val_pair = logline.text.split(' ', 1)[0]
    key, audit_msg_type = first_key_val_pair.split('=')
    if key != 'type':
        raise ValueError('Does not match expected format: %s'%logline.text)

    if audit_msg_type not in templates:
        raise KeyError("type=%s not in dictionary"%audit_msg_type)

    return TimedTemplate(logline.ts, templates[audit_msg_type])

def apply_templates(templates, loglines, mp=True, process_auditd=False):
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
        process_auditd: whether or not to use specialized auditd processing (default: False)

    Returns:
        timed_templates: a list of TimedTemplate named tuples that represent which templates occurred at which times in the log file.

    """
    # Change processing mode for auditd data
    if process_auditd:
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


def apply_events(events, windows, mp=False):
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