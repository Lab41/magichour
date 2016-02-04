from collections import Counter


def window(line, windowLen):
    '''
    make a key from the time

    Args:
        line(LogLine): a log line that has been through template processing
        windowLen(int): length of the window in seconds

    Returns:
        retVal( tuple): a (window, templateId) key value pair in tuple form
    '''

    win = int(line.ts / windowLen)
    return (win, line.templateId)


def rdd_window(sc, logLineRDD, windowLen, withCounts=False):
    '''
    read a log/directory into LogLine RDD format
    NOTE: only ts, and msg are populated
    Args:
        sc(sparkContext)
        windowLen(int): length of the window in seconds
        withCounts(boolean): return counts with the items seen within the window

    Returns:
        retval(RDD(LogLines): RDD of logs read from the LogFile URI
    '''

    if withCounts:
        win = logLineRDD.map(lambda line: window(line, windowLen))
        return win.groupByKey()\
                  .mapValues(lambda x, y: Counter(y))
    else:
        win = logLineRDD.map(lambda line: window(line, windowLen))
        return win.groupByKey()\
                  .map(lambda x, y: set(y))
