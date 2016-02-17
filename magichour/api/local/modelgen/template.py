"""
This module contains the different algorithms that were evaluated for discovering log file templates (format strings).

Add additional template processors to this file.

Functions in this module should accept an iterable of LogLines.
Functions should return an iterable of Templates.
(see named tuple definition in magichour.api.local.util.namedtuples)
"""

import re
import tempfile
import uuid

from magichour.api.local.modelgen.LogCluster import LogCluster
from magichour.api.local.util.log import get_logger, log_exc
from magichour.api.local.util.namedtuples import DistributedTemplateLine
from magichour.lib.StringMatch import StringMatch

logger = get_logger(__name__)

def logcluster(lines, *args, **kwargs):
    """
    This function uses the logcluster algorithm (available at http://ristov.github.io/logcluster/) to cluster
    log files and mine line patterns. See http://ristov.github.io/publications/cnsm15-logcluster-web.pdf for
    additional details on the algorithm. The current implementation writes loglines to a temporary file then
    feeds it to the logcluster command line tool (written in perl).

    Eventually, the goal is to fully translate logcluster.pl into python to eliminate this step.

    Behavior of this function differs depending on how of lines and file_path are set:
    lines AND file_path set: write lines to file at file_path
    lines BUT NOT file_path set: write lines to temporary file
    file_path BUT NOT lines: pass file_path directly into logcluster
    NEITHER lines NOR file_path: throw exception

    Args:
        lines: an iterable of LogLine named tuples
        *args:
        **kwargs:

    Kwargs:
        file_path (string): target path to pass to logcluster.pl (only used if lines is None, otherwise ignored).
        All other kwargs are passed on the command line to logcluster.pl. See above for details.

    Returns:
        templates: a list of Template named tuples
    """
    file_path = kwargs.pop("file_path", None)
    fp = None

    if lines and file_path:
        logger.info("Writing lines to file: %s", file_path)
        LogCluster.write_file(lines, file_path)
    elif lines and not file_path:
        fp = tempfile.NamedTemporaryFile()
        file_path = fp.name
        logger.info("Writing lines to temporary file: %s", file_path)
        LogCluster.write_file(lines, file_path)
    elif not lines and file_path:
        logger.info("Using existing lines in file: %s", file_path)
    else: #not lines and not passed_file_path
        log_exc(logger, "Must pass either argument 'lines' or keyword argument 'file_path' (or both).")

    support = kwargs.pop("support", None)
    if not support:
        log_exc(logger, "Must pass kwarg 'support'.")
    output = LogCluster.run_on_file(file_path, support, *args, **kwargs)

    if fp:
        # Temporary files are deleted when closed.
        logger.info("Closing file: %s", file_path)
        fp.close()

    templates = LogCluster.parse_output(output)
    return templates

def stringmatch(lines, *args, **kwargs):
    """
    This function uses the StringMatch algorithm to perform clustering and line pattern mining.
    See the paper "One Graph Is Worth a Thousand Logs: Uncovering Hidden Structures in Massive System Event Logs"
    by Aharon, Barash, Cohen, and Mordechai for further details on the algorithm.

    The name "StringMatch" was taken from another paper: (Aharon et al do not name their algorithm).

    Args:
        lines: (iterable LogLine): an iterable of LogLine named tuples

    Kwargs:
        batch_size (int): batch_size to pass to StringMatch (default: 5000)
        skip_count (int): skip_count to pass to StringMatch (default: 0)
        threshold (float): threshold to pass to StringMatch, must be between 0 and 1 (default: 0.75)
        min_samples (int): min_samples to pass to StringMatch (default: 25)

    Returns:
        templates (list Template): a list of Template named tuples
    """
    batch_size = kwargs.get("batch_size", 5000)
    skip_count = kwargs.get("skip_count", 0)
    threshold = kwargs.get("threshold", 0.75)
    min_samples = kwargs.get("min_samples", 25)

    clusters = StringMatch.get_clusters(lines, batch_size, skip_count, threshold, min_samples)
    template_id = 1
    templates = []
    for cluster in clusters:
        template_str = cluster.get_template_line()
        template_regex = re.compile("%s$" % re.escape(template_str))
        template = DistributedTemplateLine(
            id=str(uuid.uuid4()),
            template=template_regex,
            skip_words=None,
            raw_str=template_str,
        )
        templates.append(template)
        template_id += 1
    return templates

def baler(lines):
    """
    This function uses the Baler tool, created by Sandia National Labs.
    The tool is expected to be released in Q1 2016, so this code will be updated when that happens.

    TODO: Complete this section.

    Args:
        lines (iterable LogLine): an iterable of LogLine named tuples
    Returns:
        templates (list Template): a list of Template named tuples
    """
    pass
