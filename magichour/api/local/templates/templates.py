from subprocess import Popen, PIPE
import os
import re
import subprocess
import sys
import tempfile

from magichour.lib import StringMatch
from magichour.api.local.templates.reader import parse_logcluster
#LogLine = namedtuple("LogLine", ["t", "msg"])
#Template = namedtuple("Template", ["id", "match", "str"])

cur_dir = os.path.dirname(__file__)
LOGCLUSTER = os.path.abspath(os.path.join(cur_dir, "../../../lib/LogCluster/logcluster-0.03/logcluster.pl"))

def logcluster(lines, *args, **kwargs):   
    """
    This function uses the logcluster algorithm (available at http://ristov.github.io/logcluster/) to cluster log files and mine line patterns.
    See http://ristov.github.io/publications/cnsm15-logcluster-web.pdf for additional details on the algorithm.
    The current implementation writes loglines to a temporary file then feeds it to the logcluster command line tool (perl).
    Eventually, the goal is to fully translate logcluster.pl into python to eliminate this step.

    Args:
        lines (iterable LogLine): an iterable of LogLine named tuples

    Kwargs:
        logcluster_kwargs (dict): a dictionary containing command-line options to pass to logcluster.pl

    Returns:
        templates (list Template): a list of Template named tuples
    """
    # Write lines to temporary file.
    temp = tempfile.NamedTemporaryFile()
    for line in lines:
        temp.write("%s\n" % line.text)
   
    # Consume command-line args from kwargs['logcluster_kwargs'].
    command = ["perl", LOGCLUSTER,]
    logcluster_args = kwargs.get("logcluster_kwargs", {})
    for k, v in logcluster_args.items():
        command.append("--%s" % k)
        command.append(v)
    command.append("--input")
    command.append(temp.name)

    # Store stdout of subprocess into output. Note that stderr is still normally routed.
    output = subprocess.check_output(command)
  
    # Temp file is deleted when calling close().
    temp.close()

    templates = lc_reader._parse_logcluster(output)
    return templates

def stringmatch(lines, *args, **kwargs):
    """
    This function uses the StringMatch algorithm to perform clustering and line pattern mining.
    See the paper "One Graph Is Worth a Thousand Logs: Uncovering Hidden Structures in Massive System Event Logs" by Aharon, Barash, Cohen, and Mordechai for further details on the algorithm.

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
