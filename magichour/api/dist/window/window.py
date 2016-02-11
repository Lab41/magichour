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


def windowRDD(sc, logLineRDD, windowLen, withCounts=False):
    '''
    read a log/directory into DistributedLogLine RDD format
    NOTE: only ts, and msg are populated
    Args:
        sc(sparkContext)
        windowLen(int): length of the window in seconds
        withCounts(boolean): return counts with the items seen within the window

    Returns:
        retval(RDD(DistributedLogLines): RDD of logs read from the LogFile URI
                              NOTE: the list dedupes then return a list
                              as follow on processing takes a RDD list
    '''

    if withCounts:
        win = logLineRDD.map(lambda line: collide(line, windowLen))
        return win.groupByKey()\
                  .map(lambda (x, y): list(Counter(y).iteritems()))
    else:
        win = logLineRDD.map(lambda line: collide(line, windowLen))
        return win.groupByKey()\
                  .map(lambda (x, y): list(set(y)))
