from magichour.api.local.modelgen import template
from magichour.api.local.util.log import get_logger, log_time, log_exc
from magichour.lib.LogCluster.LogCluster import log_cluster_local
logger = get_logger(__name__)


@log_time
# file_path=logcluster_file, support=str(LOGCLUSTER_SUPPORT)
def logcluster_substep(lines, *args, **kwargs):
    logger.info("Running logcluster... (%s)", kwargs)
    #gen_templates = template.logcluster(lines, *args, **kwargs)
    gen_templates = log_cluster_local(lines, **kwargs)
    return gen_templates


@log_time
def stringmatch_substep(lines, *args, **kwargs):
    logger.info("Running stringmatch...")
    gen_templates = template.stringmatch(lines, *args, **kwargs)
    return gen_templates


@log_time
def template_step(lines, template_algorithm="logcluster", *args, **kwargs):
    CHOICES = {
        "logcluster": logcluster_substep,
        "stringmatch": stringmatch_substep}
    template_fn = CHOICES.get(template_algorithm, None)
    if not template_fn:
        log_exc(logger, "template_algorithm must be one of: %s" % CHOICES)
    gen_templates = template_fn(lines, *args, **kwargs)
    return gen_templates
