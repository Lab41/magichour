from magichour.api.dist.preprocess import rdd_ReadLog
from magichour.api.dist.preprocess import rdd_PreProcess
from magichour.lib.LogCluster import log_cluster


def templateGen_RDD(sc, logInURI, transformURI, support):
    rddLogs = rdd_ReadLog(sc, logInURI)
    pre_processedLogs = rdd_PreProcess(sc, transformURI, rddLogs)
    return log_cluster(sc, pre_processedLogs, support)
