from collections import Counter


def collide(line, windowLen):
    '''
    make a key from the time

    Args:
        line(DistributedLogLine): a log line that has been through template processing
        windowLen(int): length of the window in seconds

    Returns:
        retVal( tuple): a (window, templateId) key value pair in tuple form
    '''

    win = int(line.ts / windowLen)
    return (win, line.templateId)


def window_rdd(sc, rdd_log_lines, window_length, withCounts=False):
    '''
    read a log/directory into DistributedLogLine RDD format
    NOTE: only ts, and msg are populated
    Args:
        sc(sparkContext)
        rdd_log_lines(rdd[LogLine]): Rdd of log line objects to window
        window_length(int): length of the window in seconds
        withCounts(boolean): return counts with the items seen within the window

    Returns:
        retval(RDD(DistributedLogLines): RDD of logs read from the LogFile URI
                              NOTE: the list dedupes then return a list
                              as follow on processing takes a RDD list
    '''

    if withCounts:
        win = rdd_log_lines.map(lambda line: collide(line, window_length))
        return win.groupByKey()\
                  .map(lambda x_y: list(Counter(x_y[1]).iteritems()))
    else:
        win = rdd_log_lines.map(lambda line: collide(line, window_length))
        return win.groupByKey()\
                  .map(lambda x_y1: list(set(x_y1[1])))
