sc.addPyFile('magichour.zip')

from magichour.api.dist.templates.templateEval import templateEvalRDD

transformURI = 'hdfs://namenode/magichour/simpleTrans'
templateURI = 'hdfs://namenode/magichour/templates'
logInURI = 'hdfs://namenode/magichour/tbird.xaa.templateGenRDD'
logOUTURI = 'hdfs://namenode/magichour/tbird.xaa.templateGenRDD.templateEvalRDD'

test = templateEvalRDD(sc, logInURI, transformURI, templateURI)

test.saveAsPickleFile(logOUTURI)
