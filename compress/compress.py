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
    if name.lower().endswith('.gz'):
        return gzip.open(name, mode+'b')
    else:
        return open(name, mode)


def makeTransformedLine(l, transforms):
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
    retVal = LogLine(l.ts, l.text.lstrip().rstrip(), processed.lstrip().rstrip(), replaceDict, None)

    return retVal


def escapeCrap(x):
    return re.escape(x)


def makeReplacement(s):

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
    retVal = list()

    for o in range(0, len(l), 3):
        PATTERN = l[o].lstrip().rstrip()
        PATTERN = escapeCrap(PATTERN)
        PATTERN = makeReplacement(PATTERN)
        retVal.append(LogSupport(o/3, re.compile(PATTERN)))
        # re.compile(PATTERN).pattern is the original text
    return retVal


def readTransforms(sFile):
    retVal = list()
    for s in sFile:
        if s.lstrip()[0] == '#':
            continue
        else:
            ID, TYPE, NAME, TRANSFORM = s.lstrip().rstrip().split(',', 3)
            retVal.append(TransformLine(ID, TYPE, NAME, r''+TRANSFORM))
    return retVal


def getWordSkipNames(s, g):
    pattern = r'\(\(\?:\\ \\S\+\){(\d),(\d)}\)'
    matchObj = re.finditer(pattern, s.pattern.pattern, re.M | re.I)

    retVal = list()

    if matchObj:
        for m in matchObj:
            vals = m.groups()
            fpattern = r'((?:\ \S+){%i,%i})' % (int(vals[0]), int(vals[1]))
            retVal.append(fpattern)

    return retVal


def matchSupport(procLogLine, output, support):
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
            b = getWordSkipNames(support, a.groups())
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
    oFile.write('numSupports=%s\n' % (len(supports)))
    for s in supports:
        oFile.write('%s\n' % s.pattern.pattern)


def writeOutput(o, oFile):
    outData = '%s,%s,%s\n' % (o.ts, o.supportId, o.dictionary)
    oFile.write(outData)


def main(argv):
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

            rv = matchSupport(processedLine, sys.stdout, support)
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
