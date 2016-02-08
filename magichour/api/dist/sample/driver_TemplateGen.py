sc.addPyFile('magichour.zip')

from magichour.api.dist.templates.templateGen import templateGenRDD

transformURI = 'hdfs://namenode/magichour/simpleTrans'
support = 1000
logInURI = 'hdfs://namenode/magichour/tbird/xaa.gz'
logOutURI = 'hdfs://namenode/magichour/tbird.xaa.templateGenRDD'

test = templateGenRDD(sc, logInURI, transformURI, support)
test.saveAsPickleFile(logOutURI)
