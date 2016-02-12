from pyspark.mllib.fpm import FPGrowth


def FPGrowthRDD(transactionsRDD, minSupport=0.2, numPartitions=10):
    '''
    perform the FPGrowth algorithm
    '''
    model = FPGrowth.train(transactionsRDD, minSupport, numPartitions)
    return model.freqItemsets()
