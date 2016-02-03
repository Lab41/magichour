from magichour.api.local.modeleval import apply
from magichour.api.local.util.log import get_logger, log_time

logger = get_logger(__name__)

@log_time
def genapply_step(lines, gen_templates):
    logger.info("Applying templates to lines...")
    timed_templates = apply.apply_templates(gen_templates, lines)
    return timed_templates