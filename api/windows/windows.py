# template_timestamps = [(t, template_id), ...]
def window(template_timestamps, window_size=60):
    isFirst = True
    windows = []
    current_window = set()

    for timestamped_template in timestamped_templates:
        t, template = timestamped_template
        currentTime = math.floor(int(float(t)) /  int(window_size))
        if isFirst:
            oldTime = currentTime
            isFirst = False
        if currentTime != oldTime:
            windows.append(current_window)
            current_window = set()
        current_window.add(timestamped_template)
        currentTime = oldTime

    if current_window:
        windows.append(current_window)

    return windows
