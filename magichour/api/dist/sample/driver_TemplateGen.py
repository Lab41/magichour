sc.addPyFile('magichour.zip')

from magichour.api.dist.templates.templateGen import gen_tamplate_from_logs, read_logs_from_uri


transforms_URI = 'hdfs://namenode/magichour/simpleTrans'
raw_log_URI = 'hdfs://namenode/magichour/tbird.500k.gz'
template_output_URI = 'hdfs://namenode/magichour/templates'
support = 1000

# Read in log file RDD
# Note: You may want to set persistence to MEMORY_ONLY or
# MEMORY_AND_DISK_SER depending on data size
preprocessed_log_rdd = read_logs_from_uri(
    sc,
    raw_log_URI,
    preprocess_log=True,
    transforms_URI=transforms_URI).cache()

# Generate Templates
templates = gen_tamplate_from_logs(sc, preprocessed_log_rdd, support)

# Persist to disk for subsequent Analysis
sc.parallelize(templates, 1).saveAsPickleFile(template_output_URI)
