from magichour.api.local.util.log import get_logger, log_time
from magichour.api.local.modeleval.apply import apply_events

logger = get_logger(__name__)

@log_time
def evalapply_step(gen_events, timed_templates, **kwargs):
    logger.info("Applying events to timed templates...")
    timed_events = apply_events(gen_events, timed_templates, **kwargs)
    return timed_events
