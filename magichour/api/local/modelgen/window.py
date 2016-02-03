from magichour.api.local.util.namedtuples import ModelGenWindow
from magichour.api.local.util.window import window

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
    modelgen_windows = [ModelGenWindow(template_ids=template_ids) for window_id, template_ids in windows.iteritems()]
    return modelgen_windows

