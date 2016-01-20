import math
from collections import defaultdict

# timed_template = [(t, template_id), ...]
def window(timed_templates, window_size=60):
    windows = defaultdict(set)
    for timed_template in timed_templates:
        t, template = timed_template
        key = math.floor(int(float(t)) / int(window_size))
        windows[key].add(timed_template)
    return windows.values()

    """
    isFirst = True
    windows = []
    current_window = set()

    for timed_template in timed_templates:
        t, template = timed_template
        currentTime = math.floor(int(float(t)) / int(window_size))
        if isFirst:
            oldTime = currentTime
            isFirst = False
        if currentTime != oldTime:
            windows.append(current_window)
            current_window = set()
        current_window.add(timed_template)
        currentTime = oldTime

    if current_window:
        windows.append(current_window)

    return windows
    """
