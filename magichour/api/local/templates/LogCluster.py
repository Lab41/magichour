import os
import re
import subprocess

from magichour.api.local.named_tuples import Template
from magichour.api.local.logging_util import get_logger

logger = get_logger(__name__)

cur_dir = os.path.dirname(__file__)
LOGCLUSTER = os.path.abspath(os.path.join(cur_dir, "../../../lib/LogCluster/logcluster-0.03/logcluster.pl"))

def write_file(lines, file_path):
    with open(file_path, 'wb') as fp:
        for line in lines:
            fp.write("%s\n" % line.text)

def run_on_file(file_path, *args, **kwargs):
    command = ["perl", LOGCLUSTER,]
    #logcluster_args = kwargs.get("logcluster_kwargs", {})
    #for k, v in logcluster_args.items():
    # Consume command-line args from kwargs.
    for k, v in kwargs.items():
        command.append("--%s" % k)
        command.append(v)
    command.append("--input")
    command.append(file_path)

    logger.info("Calling subprocess: %s" % command)

    # Store stdout of subprocess into output. Note that stderr is still normally routed.
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    for err_line in p.stderr:
        logger.info(err_line.strip())
    output = p.stdout.read()
    return output

def parse_output(output):
    """
    Parses and interprets the output (from stdout) of running logcluster.pl.

    Args:
        output (string): string containing stdout output of running logcluster.pl.

    Returns:
        matches (list Template): list of Templates, created by the output of logcluster and ordered by the length of their matches.
    """
    output = output.splitlines()

    matches = list()
    template_id = 1
    for o in range(0, len(output), 3): # every 3rd line is a template
        m = output[o].strip()
        fixedLine = re.escape(m)
        replacement = _findReplacement(fixedLine).strip()
        template = Template(template_id, replacement, m)
        matches.append(template)
        template_id += 1

    # Make sure that small get done before large
    # TODO do the correct thing someday
    '''
    correct way:

    For each pair of regexes r and s for languages L(r) and L(s)
      Find the corresponding Deterministic Finite Automata M(r) and M(s)   [1]
        Compute the cross-product machine M(r x s) and assign accepting states
           so that it computes L(r) - L(s)
        Use a DFS or BFS of the the M(r x s) transition table to see if any
           accepting state can be reached from the start state
        If no, you can eliminate s because L(s) is a subset of L(r).
        Reassign accepting states so that M(r x s) computes L(s) - L(r)
        Repeat the steps above to see if it's possible to eliminate r

    '''
    simple_cmp = lambda x, y: len(y.match) - len(x.match)
    matches = sorted(matches, cmp=simple_cmp)
    matches = [Template(m.id, re.compile(m.match+'$'), m.str) for m in matches]
    return matches

def _findReplacement(s):
    # pattern = r'\*\{(\d*).(\d*)\}'
    pattern = r'\\ \\\*\\\{(\d*)\\,(\d)\\}'
    matchObj = re.finditer(pattern, s, re.M | re.I)
    b = s

    if matchObj:
        for m in matchObj:
            newString = r'(:?\ \S+){%i,%i}' % (int(m.groups()[0]),
                                               int(m.groups()[1]))
            # the r is very important
            newFound = r'\\ \\\*\\\{%i\\,%i\\}' % (int(m.groups()[0]),
                                                   int(m.groups()[1]))
            b = re.sub(newFound, newString, b)
        return b
    return s            
