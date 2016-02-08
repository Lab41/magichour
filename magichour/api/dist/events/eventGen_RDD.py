sc.addPyFile('magichour/magichour/api/dist/window/window_RDD.py')
sc.addPyFile('magichour/magichour/api/dist/FPGrowth/FPGrowth.py')

from window_RDD import rdd_window
from FPGrowth import rdd_FPGrowth


def eventGen_RDD(sc, transactions,
                 minSupport=0.2,
                 numPartitions=10,
                 windowLen=120):
    windowed = rdd_window(sc, transactions, windowLen, False)
    return rdd_FPGrowth(windowed, minSupport, numPartitions)