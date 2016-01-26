import tempfile
import re

from magichour.lib.StringMatch import StringMatch
from magichour.api.local.named_tuples import Template
from magichour.api.local.templates import LogCluster
from magichour.api.local.logging_util import get_logger

logger = get_logger(__name__)

def logcluster(lines, *args, **kwargs):
    """
    This function uses the logcluster algorithm (available at http://ristov.github.io/logcluster/) to cluster log files and mine line patterns.
    See http://ristov.github.io/publications/cnsm15-logcluster-web.pdf for additional details on the algorithm.
    The current implementation writes loglines to a temporary file then feeds it to the logcluster command line tool (perl).
    Eventually, the goal is to fully translate logcluster.pl into python to eliminate this step.

    Args:
        lines (iterable LogLine): an iterable of LogLine named tuples

    Kwargs:
        file_path (string): target path to pass to logcluster.pl (only used if lines is None, otherwise ignored).
        All other kwargs are passed on the command line to logcluster.pl. See above for details.

    Returns:
        templates (list Template): a list of Template named tuples
    """
    passed_file_path = kwargs.pop("file_path", None)

    fp = None
    if lines:
        # Write lines to temporary file for logcluster.pl.
        fp = tempfile.NamedTemporaryFile()
        file_path = fp.name
        logger.debug("Writing lines to temporary file: %s", file_path)
        LogCluster.write_file(lines, file_path)
    elif passed_file_path:
        # Use existing file path for logcluster.pl.
        file_path = passed_file_path
        logger.debug("Using existing lines in file: %s", file_path)
    else:
        raise Exception("Either (1) lines must not be None or (2) must pass keyword argument file_path.")

    output = LogCluster.run_on_file(file_path, *args, **kwargs)

    if fp:
        # Temporary files are deleted when closed.
        logger.debug("Closing file: %s", file_path)
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
        template = Template(template_id, template_regex, template_str)
        templates.append(template)
        template_id += 1
    return templates

def baler(lines):
    """
    This function uses the Baler tool, created by Sandia National Labs.
    The tool is expected to be released in Q1 2016, so this code will be updated when that happens.

    Args:
        lines (iterable LogLine): an iterable of LogLine named tuples
    Returns:
        templates (list Template): a list of Template named tuples
    """
    pass

# Add additional template processors here.
# The template processor should accept an iterable of named tuples (lines)
# It should also return
