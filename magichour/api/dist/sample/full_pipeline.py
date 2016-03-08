import pickle
from magichour.api.dist.templates.templateGen import gen_tamplate_from_logs, read_logs_from_uri
from magichour.api.dist.templates.templateEval import template_eval_rdd
from magichour.api.dist.events.eventGen import event_gen_fp_growth, event_gen_word2vec
from magichour.api.dist.events.eventEval import event_eval_rdd
from magichour.api.local.util.namedtuples import DistributedLogLine


# NOTE: magichour.zip can be generated using "git archive -o magichour.zip HEAD" from the top level of the project
sc.addPyFile('magichour.zip')

transforms_URI = 'hdfs:///magichour/simpleTrans'
raw_log_URI = 'hdfs:///magichour/tbirdManyFiles'
template_output_URI = 'hdfs:///magichour/distributedTemplateLines'
support = 1000

########################
# Read in log file RDD #
########################
# NOTE: You may want to set persistence to MEMORY_ONLY or MEMORY_AND_DISK_SER depending on data size
preprocessed_log_rdd = read_logs_from_uri(sc,
                                          raw_log_URI,
                                          preprocess_log=True,
                                          transforms_URI=transforms_URI).cache()

# Save/load if we want to bypass processing
#preprocessed_log_rdd.saveAsPickleFile('hdfs:///magichour/tbirdManyPreprocessed')
#preprocessed_log_rdd = sc.pickleFile('hdfs:///magichour/tbirdManyPreprocessed')

######################
# Generate Templates #
######################
templates = gen_tamplate_from_logs(sc, preprocessed_log_rdd, support)

##################
# Template Apply #
##################
matched_logline_URI= 'hdfs:///magichour/tbird.500.templateEvalRDD'
matched_logline_rdd = template_eval_rdd(sc, templates, preprocessed_log_rdd).cache()
# Save/load if we want to bypass processing
#matched_logline_rdd.saveAsPickleFile(matched_logline_URI)
#matched_logline_rdd = sc.pickleFile(matched_logline_URI)

##################
##  Event Gen   ##
##################
minSupport = 0.2
numPartitions = 10
windowLen = 120

# print 'FP Growth'
# fp_growth_events = event_gen_fp_growth(sc, matched_logline_rdd, minSupport, numPartitions, windowLen)
# for event in fp_growth_events:
#     print event

template_lookup = {}
for template in templates:
    template_lookup[template.id] = template.raw_str 

print '***********  Word2Vec  ***********'
word2vec_events = event_gen_word2vec(sc, matched_logline_rdd,  window_size=60)

for event in word2vec_events:
    print '--------Event %d-----------'%event.id
    for template_id in event.template_ids:    
        try:
            print template_lookup[template_id]
        except:
            print 'Unknown Template: ', template_id

# Save the event definitions locally
pickle.dump(word2vec_events, open('word2vec_events.pkl', 'wb'))
pickle.dump(event, open('event.pkl', 'wb'))

##################
##  Event Eval  ##
##################
windowSeconds = 500
found_events = event_eval_rdd(sc, matched_logline_rdd, word2vec_events, windowSeconds)

event_output_URI = 'hdfs:///magichour/events'
found_events.saveAsPickleFile(event_output_URI)
found_events_local = found_events.take(10000)


print found_events_local[:10]
