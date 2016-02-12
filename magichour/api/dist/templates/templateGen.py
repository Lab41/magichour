
from magichour.api.dist.preprocess.preProcess import preProcessRDD
from magichour.lib.LogCluster.LogCluster import log_cluster

def read_logs_from_uri(sc, log_uri, preprocess_log=True, transforms_URI=None):
    if preprocess_log and transformURI is None:
        raise ValueError('Preprocessing requires transform URI to be specified')

    raw_log_rdd = readLogRDD(sc, log_uri)
    if not preprocess_log:
        return raw_log_rdd
    else:
        return preProcessRDD(sc, transforms_URI, raw_log_rdd)


def gen_tamplate_from_logs(sc, logline_rdd, support):
    return log_cluster(sc, logline_rdd, support)
