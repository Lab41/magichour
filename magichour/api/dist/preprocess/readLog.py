from magichour.api.local.util.namedtuples import DistributedLogLine


def proc_log_line(line, logFile):
    '''
    handles the logfile specific parsing input lines into 2 parts
    ts: timestamp float
    text: the rest of the message

    Args:
        line(string): text to process
        logFile(string): hint of URI used for input
                         should use for switching parsing
                         based off different directories

    Returns:
        retval(list[string,string]): [ts, text]
    '''
    return line.strip().rstrip().split(' ', 3)[2:]


def log_line(line, log_file):
    '''
    process a log line into a RDD

    Args:
        line(string): string from the logline
        logFile(string): what URI the log lines came from,
                         eventually want to do different parsing
                         based on the base of the URI

    Returns:
        retval(DistributedLogLine): fills in the first two portions of
        the LogLine namedtuple
    '''
    l = proc_log_line(line, log_file)
    return DistributedLogLine(float(l[0]),
                              l[1],
                              None,
                              None,
                              None,
                              None,
                              None)


def read_log_rdd(sc, log_file):
    '''
    read a log/directory into LogLine RDD format
    NOTE: only ts, and text are populated
    Args:
        sc(sparkContext)
        log_file(string): URI to file toprocess

    Returns:
        retval(RDD(DistributedLogLines): RDD of logs read from the LogFile URI
    '''
    sparkLogFile = sc.textFile(log_file)

    return sparkLogFile.map(lambda line: log_line(line, log_file))
