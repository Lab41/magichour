from magichour.api.local.modelgen import events
from magichour.api.local.util.log import get_logger, log_time
from magichour.api.local.util.modelgen import tfidf_filter_events

logger = get_logger(__name__)


@log_time
def paris_substep(gen_windows, *args, **kwargs):
    logger.info("Running PARIS algorithm... (%s)", kwargs)
    gen_events = events.paris(gen_windows, *args, **kwargs)
    return gen_events


@log_time
def fp_growth_substep(gen_windows, *args, **kwargs):
    logger.info("Running fp_growth algorithm... (%s)", kwargs)
    gen_events = events.fp_growth(gen_windows, *args, **kwargs)
    return gen_events


@log_time
def glove_substep(gen_windows, *args, **kwargs):
    logger.info("Running glove/cluster algorithm... (%s)", kwargs)
    gen_events = events.glove(gen_windows, *args, **kwargs)
    return gen_events


@log_time
def event_step(gen_windows, event_algorithm="fp_growth", *args, **kwargs):
    CHOICES = {
        "fp_growth": fp_growth_substep,
        "paris": paris_substep,
        "glove": glove_substep}
    event_fn = CHOICES.get(event_algorithm, None)
    if not event_fn:
        log_exc(logger, "event_algorithm must be one of: %s" % CHOICES)
    threshold = kwargs.pop("tfidf_threshold", None)
    gen_events = event_fn(gen_windows, *args, **kwargs)

    logger.info("==========Custom post processing for sample data==========")
    if threshold is not None:
        # Note that calling this will reassign random event IDs.
        logger.info(
            "Applying a tfidf filter to each event's template_ids. (threshold = %s)",
            threshold)
        gen_events = tfidf_filter_events(gen_events, threshold)
    else:
        logger.info("Skipping tfidf filter")
    logger.info("==========End custom post processing==========")

    return gen_events
