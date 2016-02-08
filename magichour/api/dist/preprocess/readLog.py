from collections import namedtuple

LogLine = namedtuple('LogLine', ['ts', 'msg',
                                 'processed', 'dictionary',
                                 'template', 'templateId', 'templateDict'])

TemplateLine = namedtuple('TemplateLine', ['id', 'template', 'skipWords'])


TransformLine = namedtuple('TransformLine',
                           ['id', 'type', 'NAME', 'transform', 'compiled'])


def procLogLine(line, logFile):
    '''
    handles the logfile specific parsing input lines into 2 parts
    ts: timestamp float
    msg: the rest of the message

    Args:
        line(string): text to process
        logFile(string): hint of URI used for input
                         should use for switching parsing
                         based off different directories

    Returns:
        retval(list[string,string]): [ts, msg]
    '''
    return line.strip().rstrip().split(' ', 3)[2:]


def logLine(line, logFile):
    '''
    process a log line into a RDD

    Args:
        line(string): string from the logline
        logFile(string): what URI the log lines came from,
                         eventually want to do different parsing
                         based on the base of the URI

    Returns:
        retval(LogLine): fills in the first two portions of the LogLine
                         namedtuple
    '''
    l = procLogLine(line, logFile)
    return LogLine(float(l[0]),
                   l[1],
                   None,
                   None,
                   None,
                   None,
                   None)


def readLogRDD(sc, logFile):
    '''
    read a log/directory into LogLine RDD format
    NOTE: only ts, and msg are populated
    Args:
        sc(sparkContext)
        logFile(string): URI to file toprocess

    Returns:
        retval(RDD(LogLines): RDD of logs read from the LogFile URI
    '''
    sparkLogFile = sc.textFile(logFile)

    return sparkLogFile.map(lambda line: logLine(line, logFile))