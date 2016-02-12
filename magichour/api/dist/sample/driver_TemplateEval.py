sc.addPyFile('magichour.zip')

from magichour.api.dist.templates.templateEval import templateEvalRDD
from magichour.api.dist.templates.templateGen import read_logs_from_uri

# Read templates
template_output_URI = 'hdfs://namenode/magichour/templates'
templates = sc.pickleFile(template_output_URI).collect()

# Read Log Files
transforms_URI = 'hdfs://namenode/magichour/simpleTrans'
raw_log_URI = 'hdfs://namenode/magichour/tbird.500k.gz'
preprocessed_log_rdd = read_logs_from_uri(sc,
                                          raw_log_URI,
                                          preprocess_log=True,
                                          transforms_URI=transforms_URI).cache()

# Match log lines to templates
matched_logline_URI= 'hdfs://namenode/magichour/tbird.500.templateEvalRDD'
matched_logline_rdd = templateEvalRDD(sc, templates, preprocessed_log_rdd)
matched_logline_rdd.saveAsPickleFile(matched_logline_URI)
