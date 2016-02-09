sc.addPyFile('magichour.zip')

from magichour.api.dist.events.eventGen import eventGenRDD

t = 'hdfs://namenode/magichour/tbird.500.templateEvalRDD'
minSupport = 0.2
numPartitions = 10
windowLen = 120
transactions = sc.pickleFile(t)

test = eventGenRDD(sc, transactions, minSupport, numPartitions, windowLen)

test
