from magichour.api.local.util.log import get_logger, log_time
from magichour.api.local.modeleval.apply import apply_events

logger = get_logger(__name__)

@log_time
def evalapply_step(gen_events, modeleval_windows):
    logger.info("Applying events to windows...")
    timed_events = apply_events(gen_events, modeleval_windows)
    return timed_events