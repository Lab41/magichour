from magichour.api.dist.preprocess import readLog
from magichour.api.dist.preprocess import preProcess
from magichour.lib.LogCluster import log_cluster


def templateGenRDD(sc, logInURI, transformURI, support):
    rddLogs = readLogRDD(sc, logInURI)
    pre_processedLogs = preProcessRDD(sc, transformURI, rddLogs)
    return log_cluster(sc, pre_processedLogs, support)
