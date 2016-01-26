import re

from magichour.api.local.named_tuples import Template

def parse_logcluster(output):
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