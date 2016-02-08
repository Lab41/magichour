from magichour.api.dist.window.window import windowRDD
from magichour.api.dist.FPGrowth.FPGrowth import FPGrowthRDD


def eventGenRDD(sc, transactions,
             minSupport=0.2,
             numPartitions=10,
             windowLen=120):
    windowed = windowRDD(sc, transactions, windowLen, False)
    return FPGrowthRDD(windowed, minSupport, numPartitions)
