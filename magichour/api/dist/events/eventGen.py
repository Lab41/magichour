from magichour.api.dist.window import window
from magichour.api.dist.FPGrowth import FPGrowth


def eventGen_RDD(sc, transactions,
                 minSupport=0.2,
                 numPartitions=10,
                 windowLen=120):
    windowed = window(sc, transactions, windowLen, False)
    return rdd_FPGrowth(windowed, minSupport, numPartitions)
