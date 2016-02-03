from magichour.api.local.util.log import log_time
from magichour.api.local.util.namedtuples import ModelEvalWindow
from magichour.api.local.util.modelgen import logger


@log_time
def extract_template_ids(windows): # This function only works on ModelEvalWindow
    return [[timed_template.template_id for timed_template in modeleval_window.timed_templates] for modeleval_window in windows]


@log_time
def remove_junk_drawer(windows):
    modeleval_windows = []
    for window in windows:
        timed_templates = [timed_template for timed_template in window.timed_templates if timed_template.template_id != -1]
        modeleval_window = ModelEvalWindow(window.id, timed_templates)
        modeleval_windows.append(modeleval_window)
    logger.info("Removed junk drawer from ModelEvalWindows")
    return modeleval_windows