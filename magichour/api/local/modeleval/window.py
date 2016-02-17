from magichour.api.local.modelgen.window import window
from magichour.api.local.util.namedtuples import ModelEvalWindow
from magichour.api.local.util.log import get_logger

logger = get_logger(__name__)

def modeleval_window(timed_templates, window_size=60, remove_junk_drawer=False):
    windows = window(timed_templates, window_size, remove_junk_drawer, template_ids_only=False)

    modeleval_windows = []
    for window_id, timed_templates in windows.iteritems():
        # It doesn't matter which TimedTemplate we take since all in the same window will resolve to the same start/end times.
        m = timed_templates[0].ts % window_size
        start_time = timed_templates[0].ts - m
        end_time = start_time + window_size
        modeleval_windows.append(ModelEvalWindow(start_time=start_time, end_time=end_time, timed_templates=timed_templates))
    return modeleval_windows