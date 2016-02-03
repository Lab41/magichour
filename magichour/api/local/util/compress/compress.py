import re
import sys
from collections import namedtuple
import gzip

LogLine = namedtuple('LogLine', ['ts', 'text', 'processed',
                                 'dictionary', 'supportId'])
TransformLine = namedtuple('TransformLine', ['id', 'type', 'NAME', 'transform'])
LogSupport = namedtuple('LogSupport', ['supportId', 'pattern'])
OutLine = namedtuple('OutLine', ['ts', 'supportId', 'dictionary'])


def openFile(name, mode):
    '''
    wrapper for file open, will handle reading/writing gzip files

    Args:
        name(string): name of file to open, if name ends in '.gz'
                      file is treated as a gzip file for i/o
        mode(string): mode to open the file as

    Returns:
        retval(file): filehandle
    '''
    if name.lower().endswith('.gz'):
        return gzip.open(name, mode+'b')
    else:
        return open(name, mode)


def makeTransformedLine(l, transforms):
    '''
    perform a series of regex replacements on a LogLine
        store a list of pre-processing replacements in a dictionary

    Args:
        l(LogLine): namedTuple containing a logline
        transforms(list(TransformLine)): series of regex transforms to apply

    Returns:
        retval(LogLine): LogLine namedTuple with replacements made
    '''
    text = l.text.strip()
    replaceDict = dict()
    FLAGS = re.MULTILINE | re.DOTALL
    for t in transforms:
        if t.type == 'REPLACE':
            replaceList = re.findall(t.transform, text)
            if replaceList:
                replaceDict[t.NAME] = replaceList
            text = re.sub(t.transform, ' '+t.NAME+' ', text, 0, FLAGS)

        if t.type == 'REPLACELIST':
            print 'REPLACELIST not implemented yet'

    processed = ' '.join(text.split())
    retVal = LogLine(l.ts, l.text.lstrip().rstrip(),
                     processed.lstrip().rstrip(), replaceDict, None)

    return retVal


def escapeCrap(x):
    '''
    perform regex safe escapement

    Args:
        x(string): string with possibly unsafe characters

    Returns:
        retval(string): string with escapements

    '''

    return re.escape(x)


def makeReplacement(s):
    '''
    find an escaped version of skip{m,n} words
    replace with unescaped version

    Args:
        s(string): string to search

    Returns:
        retval(string): string with replacement
    '''

    pattern = r'\\ \\\*\\\{(\d*)\\,(\d)\\}'
    matchObj = re.finditer(pattern, s, re.M | re.I)
    b = s

    if matchObj:
        for m in matchObj:

            newString = r'((?:\ \S+){%i,%i})' % (int(m.groups()[0]),
                                                 int(m.groups()[1]))
            # the r is very important
            newFound = r'\\ \\\*\\\{%i\\,%i\\}' % (int(m.groups()[0]),
                                                   int(m.groups()[1]))
            b = re.sub(newFound, newString, b)
        return b


def procSupports(l):
    '''
    read the logCluser supports output file format
    turn each line into a regex so log lines can be catagorized

    Args:
        l(list(strings)): list of lines in the procSupports output file

    Returns:
        retval(list(_sre.SRE_Pattern)): list of compiled regex to search for
    '''

    retVal = list()

    for o in range(0, len(l), 3):
        PATTERN = l[o].lstrip().rstrip()
        PATTERN = escapeCrap(PATTERN)
        PATTERN = makeReplacement(PATTERN)
        retVal.append(LogSupport(o/3, re.compile(PATTERN)))
        # re.compile(PATTERN).pattern is the original text
    return retVal


def readTransforms(sFile):
    '''
    read the preprocessing transforms from file
    lines starting with a # are considered comments and are skipped

    Args:
        sFile(file): filehandle to the tranform file

    Returns:
        retval(list(TransformLine)): a listing of TransformLine named tuples
                                     each line describes a normalizaiton regex
    '''
    retVal = list()
    for s in sFile:
        if s.lstrip()[0] == '#':
            continue
        else:
            ID, TYPE, NAME, TRANSFORM = s.lstrip().rstrip().split(',', 3)
            retVal.append(TransformLine(ID, TYPE, NAME, r''+TRANSFORM))
    return retVal


def getWordSkipNames(s):
    '''
    find the skip word patterns

    Args:
        s(_sre.SRE_Pattern): compiled regex to match a logline

    Returns:
        retval(list(string)): list of the skip patterns found in s
    '''

    pattern = r'\(\(\?:\\ \\S\+\){(\d),(\d)}\)'
    matchObj = re.finditer(pattern, s.pattern.pattern, re.M | re.I)

    retVal = list()

    if matchObj:
        for m in matchObj:
            vals = m.groups()
            fpattern = r'((?:\ \S+){%i,%i})' % (int(vals[0]), int(vals[1]))
            retVal.append(fpattern)

    return retVal


def matchSupport(procLogLine, support):
    '''
    determine if the support is matched, also determine if
    there are word skip replacemnets wich need to be tracked
    for a matched logsupport line

    Args:
        procLogLine(LogLine): logline to further investigate
        support(_sre_.SRE_Pattern):

    Returns:
        retval(LogLine): logline named tuple with skip words and
        preprocessing words
        assigned to a specific support or -1 if
        no support exists
    '''

    retVal = None
    d = dict()
    ID = None
    a = support.pattern.search(procLogLine.processed)
    # print '\tsupport      ', support.pattern.pattern
    # print '\tsearching    ', procLogLine.processed
    if a:
        ID = support.supportId
        if ID == '-1':
            retVal = LogLine(procLogLine.ts,
                             procLogLine.text,
                             procLogLine.processed,
                             dict(),
                             ID)
            return retVal

        if a.groups():
            b = getWordSkipNames(support)
            # print 'b    :', b
            # print 'group:', a.groups()
            for i in range(len(b)):
                d[b[i]] = a.groups()[i]

        # print '\n\tMATCH:', support.pattern.pattern
        # print '\tMATCH:', procLogLine.processed
        # print '\tMATCH:', d

        outd = dict()
        outd.update(procLogLine.dictionary)
        outd.update(d)
        retVal = LogLine(procLogLine.ts,
                         procLogLine.text,
                         procLogLine.processed,
                         outd,
                         ID)
    return retVal


def writeHeader(supports, oFile):
    '''
    write the format strings in order

    Args:
        supports(list(_sre.SRE_Pattern)): list of compiled regex
        oFile(file): file handle for io

    Returns:
        None
    '''
    oFile.write('numSupports=%s\n' % (len(supports)))
    for s in supports:
        oFile.write('%s\n' % s.pattern.pattern)


def writeOutput(o, oFile):
    '''
    Write arguments to the output file

    Args:
        o(OutLine): namedTuple to output
        oFile(file): filehandle for io

    Returns:
        None
    '''
    outData = '%s,%s,%s\n' % (o.ts, o.supportId, o.dictionary)
    oFile.write(outData)


def main(argv):
    '''
    create a section of format strings [header]
    followed by section of
    timestamp,formatstringID,args [data]

    use the supports from LogCluster, and the preprocessing rules
    to generate a listing of format strings for the header.

    for each line of the loglines, find the replacemnts which would
    be made, along with the skip words.  store the timestamp for the
    original message, a reference to the format string, and the arguments
    needed to fill in the format string.

    Currently storing a dict(list), could save space by storing things in
    usage order instead.. also could save space by using real integers
    instead of string representations of integers.

    [header]
    number of headerValues
    header value1
    ...
    header valueN
    [format args]
    timestamp,headerID (index to header), args

    Args:
        argv(list(string)): arguments sent to the program

    Returns:
        None

    '''
    logLines = openFile(argv[0], 'r')
    logSupports = openFile(argv[1], 'r')
    simpleTransforms = openFile(argv[2], 'r')

    transforms = readTransforms(simpleTransforms)
    simpleTransforms.close()

    temp = logSupports.readlines()
    logSupports.close()

    supports = procSupports(temp)

    writeHeader(supports, sys.stdout)
    for l in logLines.readlines():
        EPOCH, LOGTEXT = l.lower().lstrip().rstrip().split(' ', 1)
        work = LogLine(EPOCH, LOGTEXT, None, None, None)
        processedLine = makeTransformedLine(work, transforms)

        madeOutput = False

        # find which support maches the logline
        for support in supports:

            rv = matchSupport(processedLine, support)
            if rv:
                outData = OutLine(rv.ts, rv.supportId, rv.dictionary)
                writeOutput(outData, sys.stdout)
                madeOutput = True
                break

        if not madeOutput:
            # no template found
            outData = OutLine(processedLine.ts, '-1', processedLine.text)
            writeOutput(outData, sys.stdout)

if __name__ == '__main__':
    main(sys.argv[1:])
