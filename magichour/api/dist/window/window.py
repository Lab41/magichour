from collections import Counter
from math import floor


def collide(line, window_length, window_overlap=None):
    '''
    make a key from the time

    Args:
        line(DistributedLogLine): a log line that has been through template processing
        window_length(int): length of the window in seconds
        window_overlap (float): fraction of window where log msgs should go in both windows
    Returns:
        retVal( tuple): a (window, templateId) key value pair in tuple form
    '''
    output = []
    window = float(line.ts)/window_length

    output.append((int(window), line.templateId))
    if window_overlap:
        delta = window - floor(window)
        # Since we are truncating near the window boundary can can be close
        # to zero or close to 1
        if delta <= window_overlap or delta >= 1-window_overlap:
            if delta > 0:
                # Also output to previous window
                output.append((int(window)-1, line.templateId))
            elif delta < 0:
                # Also output to next window
                output.append((int(window)+1, line.templateId))
    return output


def window_rdd(sc, rdd_log_lines, window_length, fine_grained_window=None, withCounts=False):
    '''
    read a log/directory into DistributedLogLine RDD format
    NOTE: only ts, and msg are populated
    Args:
        sc(sparkContext)
        rdd_log_lines(rdd[LogLine]): Rdd of log line objects to window
        window_length(int): length of the window in seconds
        fine_grained_window (int): Time in seconds near the boundary where msgs should
                                    go in both windows
        withCounts(boolean): return counts with the items seen within the window

    Returns:
        retval(RDD(DistributedLogLines): RDD of logs read from the LogFile URI
                              NOTE: the list dedupes then return a list
                              as follow on processing takes a RDD list
    '''

    if fine_grained_window:
        window_overlap = float(fine_grained_window)/window_length
    else:
        window_overlap = None

    if withCounts:
        win = rdd_log_lines.flatMap(lambda line: collide(line, window_length, window_overlap))
        return win.groupByKey()\
                  .map(lambda x_y: list(Counter(x_y[1]).iteritems()))
    else:
        win = rdd_log_lines.map(lambda line: collide(line, window_length, window_overlap))
        return win.groupByKey()\
                  .map(lambda x_y1: list(set(x_y1[1])))
