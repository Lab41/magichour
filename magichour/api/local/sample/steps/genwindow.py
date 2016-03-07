from magichour.api.local.modelgen import window
from magichour.api.local.util import modelgen
from magichour.api.local.util.log import get_logger, log_time

logger = get_logger(__name__)


@log_time
def genwindow_step(eval_loglines, *args, **kwargs):
    window_size = kwargs.pop("window_size", 60)
    remove_junk_drawer = kwargs.pop("remove_junk_drawer", True)
    logger.info("Creating model gen windows from timed_templates...")
    gen_windows = window.modelgen_window(
        eval_loglines,
        window_size=window_size,
        remove_junk_drawer=remove_junk_drawer)

    logger.info("==========Custom post processing for sample data==========")
    if not remove_junk_drawer:
        # TODO: is this code still needed? since we remove junk_drawer above by
        # default...
        logger.info(
            "Removing junk drawer entries from each window's template_ids. (template_id = -1)")
        gen_windows = modelgen.remove_junk_drawer(gen_windows)

    logger.info("Removing duplicate entries from each window's template_ids.")
    gen_windows = modelgen.uniqify_windows(gen_windows)

    threshold = kwargs.pop("tfidf_threshold", None)
    if threshold is not None:
        logger.info(
            "Applying a tfidf filter to each window's template_ids. (threshold = %s)",
            threshold)
        gen_windows = modelgen.tf_idf_filter_window(gen_windows, threshold)
    else:
        logger.info("Skipping tfidf filter")
    logger.info("==========End custom post processing==========")

    return gen_windows
