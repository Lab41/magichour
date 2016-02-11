sc.addPyFile('magichour.zip')

from magichour.api.dist.events.eventGen import event_gen_fp_growth, event_gen_word2vec

logLineURI = 'hdfs://namenode/magichour/tbird.500.templateEvalRDD'
outputPath = 'hdfs://namenode/magichour/tbird.500.eventsRDD'
minSupport = 0.2
numPartitions = 10
windowLen = 120
log_lines = sc.pickleFile(logLineURI)

print 'FP Growth'
fp_growth_events = event_gen_fp_growth(sc, log_lines, minSupport, numPartitions, windowLen)
for event in fp_growth_events:
    print event


print 'Word2Vec'
word2vec_events = event_gen_word2vec(sc, log_lines,  window_size=60)
for event in word2vec_events:
    print event


# Save to hdfs
if outputPath:
    sc.parallelize(word2vec_events).saveAsPickleFile(outputPath, batchSize=1)