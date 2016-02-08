sc.addPyFile('magichour.zip')

from magichour.api.dist.events.eventGen import eventGenRDD

transactions = 'hdfs://namenode/magichour/tbird.xaa.templateGenRDD'
outURI = 'hdfs://namenode/magichour/tbird.xaa.templateGenRDD.eventGenRDD'
minSupport = 0.2
numPartitions = 10
windowLen = 120

test = eventGenRDD(sc, transactions, minSupport, numPartitions, windowLen)

test.savePickleFile(outURI)
