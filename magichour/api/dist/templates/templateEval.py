from magichour.api.dist.preprocess.readLog import readLogRDD
from magichour.api.dist.preprocess.preProcess import preProcessRDD

from collections import namedtuple
from collections import defaultdict
import re

LogLine = namedtuple('LogLine', ['ts', 'msg',
                                 'processed', 'dictionary',
                                 'template', 'templateId', 'templateDict'])

TemplateLine = namedtuple('TemplateLine', ['id', 'template', 'skipWords'])


TransformLine = namedtuple('TransformLine',
                           ['id', 'type', 'NAME', 'transform', 'compiled'])


def badWay(r1, r2):
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

    return(len(r2)-len(r1))


def rankMatches(m):
    '''
    sort maches according to custom sort

    Args:
        m(list(string)): eventually will be used as regex

    Returns:
        retval(list(string)): sorted array
    '''
    retval = sorted(m, cmp=badWay)
    return retval


def getWordSkipNames(s):
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
            fpattern = r'((?:\ {0,1}\S+){%i,%i})' % (int(vals[0]), int(vals[1]))
            retVal.append(fpattern)

    return retVal


def readTemplates(sc, templateFile):
    '''
    returns a list of regex for replacement processing

    Args:
        sc(sparkContext): spark context
        templateFile(string): uri to the transform file in HDFS

    Returns:
        retval(list(TemplateLine)) list of template lines
    '''

    # map the templateFile
    templates = sc.textFile(templateFile)

    templateRDD = templates.collect()

    matches = list()

    for t in templateRDD:
        stripped = r''+t.strip().rstrip()
        escaped = re.escape(stripped)
        replaced = unescapeSkips(escaped)
        matches.append(replaced)

    matches = rankMatches(matches)

    templateLines = list()
    for index, m in enumerate(matches):
        # match end of line too
        t = TemplateLine(index,
                         re.compile(m + '$'),
                         getWordSkipNames(re.compile(m)))
        templateLines.append(t)

    return templateLines


def unescapeSkips(s):
    '''
    find an escaped version of skip{m,n} words
    replace with unescaped version

    Args:
        s(string): string to search

    Returns:
        retval(string): string with replacement
    '''

    pattern = r'\\\(\\\:\\\?\\\ S\\\+\\\)\\\{(\d)\\\,(\d)\\\}'

    matchObj = re.finditer(pattern, s, re.M | re.I)
    b = s

    if matchObj:
        for m in matchObj:

            newString = r'((?:\ {0,1}\S+){%i,%i})' % (int(m.groups()[0]),
                                                      int(m.groups()[1]))

            # the r is very important
            newFound = r'\\\(\\:\\\?\\ S\\\+\\\)\\\{%i\\,%i\\\}' % (int(m.groups()[0]),
                                                                    int(m.groups()[1]))
            b = re.sub(newFound, newString, b)

        return b
    return s


def matchLine(line, templates):
    '''
    assign a log line to a templateId or -1 if no match
    keep track of any skip word replacements, return additional
    informaiton in the LogLine named tuple

    Args:
        line(LogLine): logline being classified
        templates(list(TemplateLine)): templates to attempt to match to
                                       broadcast variable
    Returns:
        retval(LogLine): LogLine  with the final 3 fields filled in
                         template - actual template used for match
                         templateId - number of the template
                         templateDict- dictionary of skip word replacements
    '''

    for templateLine in templates.value:
        skipFound = templateLine.template.search(line.processed)
        templateDict = defaultdict(list)

        # TODO double check that the defaultdict is working as expected
        if skipFound:
            for i in range(len(templateLine.skipWords)):
                    templateDict[templateLine.skipWords[i]].append(skipFound.groups()[i])

            return LogLine(line.ts,
                           line.msg,
                           line.processed,
                           line.dictionary,
                           templateLine.template.pattern,
                           templateLine.id,
                           templateDict)

    # could not find a template match
    return LogLine(line.ts,
                   line.msg,
                   line.processed,
                   line.dictionary,
                   None,
                   -1,
                   templateDict)


def matchTemplates(sc, templateFile, rddLogLine):
    '''
    assign a line to a template, keeping track of replacements as it goes

    Args:
        sc(sparkContext):
        templateFile(string): URI to the template file
        rddLogLine(RDD(LogLine)): RDD of LogLines to assign
    Returns:
        retval(RDD(LogLine)): additional fields of the LogLine named tuple
                              filled in, specifically
                              template,templateId,templateDict
    '''

    templates = readTemplates(sc, templateFile)
    templateBroadcast = sc.broadcast(templates)
    return rddLogLine.map(lambda line: matchLine(line, templateBroadcast))


def templateEvalRDD(sc, logInURI, transformURI, templateURI):
    rddLogs = readLogRDD(sc, logInURI)
    pre_processedLogs = preProcessRDD(sc, transformURI, rddLogs)
    return matchTemplates(sc, templateURI, pre_processedLogs)
