sc.addPyFile('magichour.zip')

from magichour.api.dist.templates.templateEval import templateEvalRDD

transformURI = 'hdfs://namenode/magichour/simpleTrans'
templateURI = 'hdfs://namenode/magichour/templates'
logInURI = 'hdfs://namenode/magichour/tbird.500k.gz'
logOUTURI = 'hdfs://namenode/magichour/tbird.500.templateEvalRDD'

test = templateEvalRDD(sc, logInURI, transformURI, templateURI)

test.saveAsPickleFile(logOUTURI)
