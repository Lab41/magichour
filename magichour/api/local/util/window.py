import math
from collections import defaultdict


def window(timed_templates, window_size=60, remove_junk_drawer=False, template_ids_only=False):
    windows = defaultdict(list)
    for timed_template in timed_templates:
        t, _, __ = timed_template
        key = math.floor(int(float(t)) / int(window_size))
        if not remove_junk_drawer or (remove_junk_drawer and timed_template.template_id != -1):
            if template_ids_only:
                windows[key].append(timed_template.template_id)
            else:
                windows[key].append(timed_template)
    return windows