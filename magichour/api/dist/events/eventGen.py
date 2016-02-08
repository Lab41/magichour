from magichour.api.dist.window import window
from magichour.api.dist.FPGrowth import rdd_FPGrowth


def eventGen_RDD(sc, transactions,
                 minSupport=0.2,
                 numPartitions=10,
                 windowLen=120):
    windowed = rdd_window(sc, transactions, windowLen, False)
    return rdd_FPGrowth(windowed, minSupport, numPartitions)
