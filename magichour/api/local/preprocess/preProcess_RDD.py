from collections import namedtuple
import re

LogLine = namedtuple('LogLine', ['ts', 'msg',
                                 'processed', 'dictionary',
                                 'template', 'templateId', 'templateDict'])

TemplateLine = namedtuple('TemplateLine', ['id', 'template', 'skipWords'])


TransformLine = namedtuple('TransformLine',
                           ['id', 'type', 'NAME', 'transform', 'compiled'])


def rdd_TransformLine(line):
    '''
    process transformations into RDD format

    Args:
        line(string): line from the transform defintion file.
                      lines beginning with # are considered comments
                      and will need to be removed
    Returns:
        retval(TransformLine): namedTuple representation of the tasking
    '''

    if line.lstrip()[0] != '#':
        # id,type,name,transform
        l = line.lstrip().rstrip().split(',', 3)
        return TransformLine(int(l[0]),
                             l[1],
                             l[2],
                             l[3],
                             re.compile(l[3]))
    else:
        return TransformLine('COMMENT',
                             'COMMENT',
                             'COMMENT',
                             'COMMENT',
                             'COMMENT')


def lineRegexReplacement(line, logTrans):
    '''
    apply a list of regex replacements to a line, make note of
    all the remplacements peformed in a dictionary(list)

    Args:
        line(LogLine): logline to work on

    Globals:
        transforms(RDD(TransformLine)): replacemnts to make with

    Returns:
        retval(LogLine): logline with the processed, and dictionary portions
                         filled in
    '''

    text = line.msg.strip()
    replaceDict = dict()

    for t in logTrans.value:
        if t.type == 'REPLACE':
            replaceList = t.compiled.findall(text)
            if replaceList:
                replaceDict[t.NAME] = replaceList
            text = t.compiled.sub(t.NAME, text, 0)

        if t.type == 'REPLACELIST':
            print 'REPLACELIST not implemented yet'

    processed = ' '.join(text.split())
    retVal = LogLine(line.ts,
                     line.msg.lstrip().rstrip(),
                     processed.lstrip().rstrip(),
                     replaceDict,
                     None,
                     None,
                     None)

    return retVal


def readTransforms(sc, transFile):
    '''
    returns a list of transforms for replacement processing

    Args:
        sc(sparkContext): spark context
        transFile(string): uri to the transform file in HDFS

    Returns:
        retval(list(TransformLine))
    '''

    # map the transFile
    simpleTransformations = sc.textFile(transFile)

    # parse loglines
    logTransforms = simpleTransformations.map(rdd_TransformLine).cache()

    trans = logTransforms.collect()

    lTrans = list()

    for t in trans:
        if t.id != 'COMMENT':
            lTrans.append(t)

    return lTrans


def logPreProcess(sc, logTrans, rrdLogLine):
    '''
    take a series of loglines and pre-process the lines
    replace ipaddresses, directories, urls, etc with constants
    keep a dictionary of the replacements done to the line

    Args:
        sc(sparkContext): spark context
        logTrans(string): location fo the transFile in HDFS
        logFile(string): location of the log data in HDFS

    Returns:
        retval(RDD(LogLines)): preprocessed log lines ready for next
                               stage of processing
   '''

    # following done to make sure that the broadcast gets to the function
    return rrdLogLine.map(lambda line: lineRegexReplacement(line, logTrans))


def rdd_preProcess(sc, logTrans, rrdLogLine):
    '''
    make a rdd of preprocessed loglines

     Args:
            sc(sparkContext): sparkContext
            logTrans(string): location fo the transFile in HDFS
            logFile(string): location of the log data in HDFS

    Returns:
            retval(RDD(LogLines)): preprocessed log lines ready for next
                                   stage of processing
    '''

    lTrans = readTransforms(sc, logTrans)
    logTrans = sc.broadcast(lTrans)
    return logPreProcess(sc, logTrans, rrdLogLine)
