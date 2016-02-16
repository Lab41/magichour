from magichour.api.local.util.namedtuples import DistributedLogLine
from magichour.api.local.util.namedtuples import DistributedTemplateLine

from collections import defaultdict
import re
import json


def bad_way(r1, r2):
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

    return(len(r2) - len(r1))


def rank_matches(m):
    '''
    sort maches according to custom sort

    Args:
        m(list(string)): eventually will be used as regex

    Returns:
        retval(list(string)): sorted array
    '''
    retval = sorted(m, cmp=bad_way)
    return retval


def get_word_skip_names(s):
    '''
    find the skip word patterns

    Args:
        s(_sre.SRE_Pattern): compiled regex to match a logline

    Returns:
        retval(list(string)): list of the skip patterns found in s
    '''

    pattern = r'\(\(\?\:\\\ \{0,1\}\\S\+\)\{(\d)\,(\d)\}\)'
    matchObj = re.finditer(pattern, s.pattern, re.M | re.I)

    retVal = list()

    if matchObj:
        for m in matchObj:
            vals = m.groups()
            fpattern = r'((?:\ {0,1}\S+){%i,%i})' % (
                int(vals[0]), int(vals[1]))
            retVal.append(fpattern)

    return retVal


def read_templates(template_list):
    '''
    returns a list of regex for replacement processing

    Args:
        template_list(list(string)): List of templates to transform into distributed log lines

    Returns:
        retval(list(DistributedTemplateLine)) list of template lines
    '''


    match_to_raw_str = dict()
    matches = list()
    for t in template_list:
        stripped = r'' + t.strip().rstrip()
        escaped = re.escape(stripped)
        replaced = unescape_skips(escaped)
        matches.append(replaced)
        match_to_raw_str[replaced] = t.strip()

    matches = rank_matches(matches)

    template_lines = list()
    for index, m in enumerate(matches):
        # match end of line too
        t = DistributedTemplateLine(id=index,
                                    template=re.compile(m + '$'),
                                    skip_words=get_word_skip_names(re.compile(m)),
                                    raw_str=match_to_raw_str[m])
        template_lines.append(t)

    return template_lines


def unescape_skips(s):
    '''
    find an escaped version of skip{m,n} words
    replace with unescaped version

    Args:
        s(string): string to search

    Returns:
        retval(string): string with replacement
    '''

    pattern = r'\\\(\\\:\\\?\\\ S\\\+\\\)\\\{(\d)\\\,(\d)\\\}'

    match = re.finditer(pattern, s, re.M | re.I)
    b = s

    if match:
        for m in match:

            newString = r'((?:\ {0,1}\S+){%i,%i})' % (int(m.groups()[0]),
                                                      int(m.groups()[1]))

            # the r is very important
            newFound = r'\\\(\\:\\\?\\ S\\\+\\\)\\\{%i\\,%i\\\}' % (
                int(m.groups()[0]), int(m.groups()[1]))
            b = re.sub(newFound, newString, b)

        return b
    return s


def match_line(line, templates):
    '''
    assign a log line to a templateId or -1 if no match
    keep track of any skip word replacements, return additional
    informaiton in the LogLine named tuple

    Args:
        line(LogLine): logline being classified
        templates(list(DistributedTemplateLine)): templates to attempt to match to
                                       broadcast variable
    Returns:
        retval(LogLine): LogLine  with the final 3 fields filled in
                         template - actual template used for match
                         templateId - number of the template
                         template_dict- dictionary of skip word replacements
    '''

    for template_line in templates.value:
        skipFound = template_line.template.search(line.processed)
        template_dict = defaultdict(list)

        # TODO double check that the defaultdict is working as expected
        if skipFound:
            for i in range(len(template_line.skip_words)):
                template_dict[
                    template_line.skip_words[i]].append(
                    skipFound.groups()[i])

            return DistributedLogLine(line.ts,
                                      line.text,
                                      line.processed,
                                      json.dumps(line.proc_dict),
                                      template_line.template.pattern,
                                      template_line.id,
                                      json.dumps(template_dict))

    # could not find a template match
    return DistributedLogLine(line.ts,
                              line.text,
                              line.processed,
                              json.dumps(line.proc_dict),
                              None,
                              -1,
                              json.dumps(template_dict))


def match_templates(sc, templates, rdd_log_lines):
    '''
    assign a line to a template, keeping track of replacements as it goes

    Args:
        sc(sparkContext):
        templates(list(DistributedTemplateLine)): List of DistributedTemplateLine objects
        rddLogLine(RDD(LogLine)): RDD of LogLines to assign
    Returns:
        retval(RDD(LogLine)): additional fields of the LogLine named tuple
                              filled in, specifically
                              template,templateId,templateDict
    '''

    template_broadcast = sc.broadcast(templates)
    return rdd_log_lines.map(lambda line: match_line(line, template_broadcast))


def template_eval_rdd(sc, templates, rdd_log_lines):
    return match_templates(sc, templates, rdd_log_lines)
