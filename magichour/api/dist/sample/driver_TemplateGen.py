sc.addPyFile('magichour.zip')

from magichour.api.dist.templates.templateGen import templateGenRDD

transformURI = 'hdfs://namenode/magichour/simpleTrans'
logInURI = 'hdfs://namenode/magichour/tbird.500k.gz'
support = 1000

test = templateGenRDD(sc, logInURI, transformURI, support)

for i in test:
    print ' '.join(i)
