sc.addPyFile('magichour.zip')
from magichour.api.dist.events.eventEval import eventEvalRDD
from magichour.api.local.util.namedtuples import DistributedLogLine


logLineURI = 'hdfs://namenode/magichour/tbird.500.templateEvalRDD'
rddlogLines = sc.pickleFile(logLineURI)


eventDefURI = 'hdfs://namenode/magichour/tbird.500.eventsRDD'
eventDefs = sc.pickleFile(eventDefURI).collect()
windowSeconds = 500
test = eventEvalRDD(sc, rddlogLines, eventDefs, windowSeconds)

test.collect()
