from magichour.api.dist.preprocess import readLog
from magichour.api.dist.preprocess import preProcess
from magichour.lib.LogCluster import log_cluster


def templateGen(sc, logInURI, transformURI, support):
    rddLogs = readLog(sc, logInURI)
    pre_processedLogs = preProcess(sc, transformURI, rddLogs)
    return log_cluster(sc, pre_processedLogs, support)
