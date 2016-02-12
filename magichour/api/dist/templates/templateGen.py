from magichour.api.dist.preprocess.readLog import readLogRDD
from magichour.api.dist.preprocess.preProcess import preProcessRDD
from magichour.lib.LogCluster.LogCluster import log_cluster

def read_logs_from_uri(sc, log_uri, preprocess_log=True, transforms_URI=None):
    """
    Read raw log lines from a text file and optionally preprocess them

    Args:
        sc: Spark Context
        log_uri (str): URI defining the location of the log files
        preprocess_log (bool): Whether or not to preprocess the logs before returning
        transforms_URI (str): String defining the location of the transforms definition

    Returns:
        log_lines(rdd(DistributedLogLine)): RDD containing log lines (optionally preprocessed)
    """
    if preprocess_log and transforms_URI is None:
        raise ValueError('Preprocessing requires transform URI to be specified')

    raw_log_rdd = readLogRDD(sc, log_uri)
    if not preprocess_log:
        return raw_log_rdd
    else:
        return preProcessRDD(sc, transforms_URI, raw_log_rdd)


def gen_tamplate_from_logs(sc, logline_rdd, support):
    """
    Generate template definitions from log lines

    Args:
        sc: Spark Context
        logline_rdd (rdd(str): URI defining the location of the log files
        preprocess_log (bool): Whether or not to preprocess the logs before returning
        transforms_URI (str): String defining the location of the transforms definition

    Returns:
        log_lines(rdd(DistributedLogLine)): RDD containing log lines (optionally preprocessed)
    """
    return log_cluster(sc, logline_rdd, support)
