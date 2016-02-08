sc.addPyFile('magichour/magichour/api/dist/preprocess/readLog_RDD.py')
sc.addPyFile('magichour/magichour/api/dist/preprocess/preProcess_RDD.py')
sc.addPyFile('magichour/magichour/lib/LogCluster/LogCluster.py')

from readLog_RDD import rdd_ReadLog
from preProcess_RDD import rdd_preProcess
from LogCluster import log_cluster


def templateGen_RDD(sc, logInURI, transformURI, support):
    rddLogs = rdd_ReadLog(sc, logInURI)
    pre_processedLogs = rdd_preProcess(sc, transformURI, rddLogs)
    return log_cluster(sc, pre_processedLogs, support)