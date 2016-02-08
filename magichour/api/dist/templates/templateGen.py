from magichour.api.dist.preprocess.readLog import readLogRDD
from magichour.api.dist.preprocess.preProcess import preProcessRDD
from magichour.lib.LogCluster.LogCluster import log_cluster


def templateGenRDD(sc, logInURI, transformURI, support):
    rddLogs = readLogRDD(sc, logInURI)
    pre_processedLogs = preProcessRDD(sc, transformURI, rddLogs)
    return log_cluster(sc, pre_processedLogs, support)
