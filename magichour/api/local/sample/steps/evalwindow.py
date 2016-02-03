from magichour.api.local.modeleval.window import modeleval_window
from magichour.api.local.util.log import get_logger, log_time

logger = get_logger(__name__)

@log_time
def evalwindow_step(timed_templates, *args, **kwargs):
    logger.info("Creating model eval windows from timed_templates...")
    eval_windows = modeleval_window(timed_templates, *args, **kwargs)
    return eval_windows