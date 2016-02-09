from magichour.api.dist.events.eventEval import eventEvalRDD
from collections import namedtuple
from random import randint

LogLine = namedtuple('LogLine', ['ts', 'msg',
                                 'processed', 'dictionary', 'supportId'])

logList = list()

for i in range(1000):
    a = LogLine(int(i), 'message=%i' % i,
                None,
                None,
                int(randint(1, 5)))
    logList.append(a)

rddlogLines= sc.parallelize(logList)

sc.addPyFile('magichour.zip')


eventDefs = 'hdfs://namenode/magichour/eventDefs'
windowSeconds = 500
test = eventEvalRDD(sc, rddlogLines, eventDefs, windowSeconds)

test.collect()
