import math
from collections import defaultdict


# timed_template = [(t, template_id), ...]
def modelgen_window(timed_templates, window_size=60, remove_junk_drawer=False):
    """
    This function was written to take in the output of the apply_template function.
    It groups template occurrences into "windows" (aka transactions) that will be passed on to a
    market basket analysis algorithm in events/events.py.

    By default the window size is 60 seconds.

    Args:
        timed_templates: iterable of timed_templates

    Kwargs:
        window_size: # of seconds to allow for each window size (default: 60)

    Returns:
        windows: list of sets containing TimedTemplate named tuples
    """

    windows = window(timed_templates, window_size, remove_junk_drawer, template_ids_only=True)
    return [template_ids for window_id, template_ids in windows.iteritems()]


def window(timed_templates, window_size=60, remove_junk_drawer=False, template_ids_only=False, sort_windows=True):
    windows = defaultdict(list)

    if sort_windows:
        # TODO: This should probably be done on the output windows...
        timed_templates = sorted(timed_templates, key=lambda x: x.ts)

    for timed_template in timed_templates:
        t, _, __ = timed_template
        key = math.floor(int(float(t)) / int(window_size))
        if not remove_junk_drawer or (remove_junk_drawer and timed_template.template_id != -1):
            if template_ids_only:
                windows[key].append(timed_template.template_id)
            else:
                windows[key].append(timed_template)

    return windows