import math
from collections import defaultdict


def modelgen_window(eval_loglines, window_size=60, remove_junk_drawer=False):
    """
    This function was written to take in the output of the apply_template function.
    It groups template occurrences into "windows" (aka transactions) that will be passed on to a
    market basket analysis algorithm in events/events.py.

    By default the window size is 60 seconds.

    Args:
        eval_loglines: iterable of timed_templates

    Kwargs:
        window_size: # of seconds to allow for each window size (default: 60)

    Returns:
        windows: list of sets containing TimedTemplate named tuples
    """

    windows = window(eval_loglines, window_size, remove_junk_drawer, template_ids_only=True)
    return [template_ids for window_id, template_ids in windows.iteritems()]


def window(eval_loglines, window_size=60, remove_junk_drawer=False, template_ids_only=False, sort_windows=True):
    windows = defaultdict(list)

    if sort_windows:
        # TODO: This should probably be done on the output windows...
        eval_loglines = sorted(eval_loglines, key=lambda x: x.ts)

    for eval_logline in eval_loglines:
        t = eval_logline.ts
        key = math.floor(int(float(t)) / int(window_size))
        if not remove_junk_drawer or (remove_junk_drawer and eval_logline.templateId != -1):
            if template_ids_only:
                windows[key].append(eval_logline.templateId)
            else:
                windows[key].append(eval_logline)
    return windows