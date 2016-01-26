from subprocess import Popen, PIPE
import os
import re
import subprocess
import sys
import tempfile
#from collections import namedtuple
#from StringMatch import StringMatch as sm

from magichour.api.local.named_tuples import LogLine, Template
#LogLine = namedtuple("LogLine", ["t", "msg"])
#Template = namedtuple("Template", ["id", "match", "str"])
from magichour.lib import StringMatch

cur_dir = os.path.dirname(__file__)
LOGCLUSTER = os.path.abspath(os.path.join(cur_dir, "../../../lib/LogCluster/logcluster-0.03/logcluster.pl"))

# Accepts iterable of namedtuples -- all must be logline namedtuples
# kwargs --> key "logcluster_kwargs" is a dict containing commandline args for logcluster.pl

# Right now this will write var lines to a file in order to feed it into logcluster.pl
# Eventually, the goal is to fully translate logcluster.pl into python in order to eliminate this step.
def logcluster(lines, *args, **kwargs):
    def _parse_logcluster(output):
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
    
    #rite lines to temporary file.
    temp = tempfile.TemporaryFile()
    for line in lines:
        temp.write("%s\n" % line.text)
    
    #command = ["perl", "./logcluster-0.03/logcluster.pl", "--lfilter", self.lfilter,
    #               "--template", self.template, "--support", str(self.support), "--input", self.filepath]
    command = ["perl", LOGCLUSTER,]
    logcluster_args = kwargs.get("logcluster_kwargs", {})
    for k, v in logcluster_args.items():
        command.append("--%s" % k)
        command.append(v)
    command.append("--input")
    command.append(filepath)

    output = subprocess.check_output(command)
   
    temp.close()

    templates = _parse_logcluster(output)
    return templates

def stringmatch(lines, *args, **kwargs):
    batch_size = kwargs.get("batch_size", 5000)
    skip_count = kwargs.get("skip_count", 0)
    threshold = kwargs.get("threshold", 0.75)
    min_samples = kwargs.get("min_samples", 25)

    clusters = sm.get_clusters(lines, batch_size, skip_count, threshold, min_samples)
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
    pass

# Add additional template processors here.
# The template processor should accept an iterable of named tuples (lines)
# It should also return  
