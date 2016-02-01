import math
from collections import defaultdict

# timed_template = [(t, template_id), ...]
def window(timed_templates, window_size=60, remove_junk_drawer=False):
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
    windows = defaultdict(list)
    for timed_template in timed_templates:
        t, template = timed_template
        key = math.floor(int(float(t)) / int(window_size))
        if not remove_junk_drawer or (remove_junk_drawer and timed_template.template_id != -1):
            windows[key].append(timed_template)
    return windows.values()
