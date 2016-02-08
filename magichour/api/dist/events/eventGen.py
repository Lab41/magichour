from magichour.api.dist.window import window
from magichour.api.dist.FPGrowth import mlFPGrowth


def eventGen(sc, transactions,
             minSupport=0.2,
             numPartitions=10,
             windowLen=120):
    windowed = window(sc, transactions, windowLen, False)
    return mlFPGrowth(windowed, minSupport, numPartitions)
