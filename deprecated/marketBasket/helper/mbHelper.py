import sys
import math
from collections import namedtuple
import gzip

iDat = namedtuple('iDat', ['time', 'cluster', 'record'])
oDat = namedtuple('oDat', ['transaction', 'cluster'])


def openFile(name, mode):
    if name.lower().endswith('.gz'):
        return gzip.open(name, mode + 'b')
    else:
        return open(name, mode)


def outputSet(oFile, cSet, transaction):
    oFile.write('%s,%s\n' % (transaction, ','.join(str(s) for s in cSet)))


def main(argv):
    iFile = openFile(argv[0], 'r')
    oFile = openFile(argv[1], 'w')
    seconds = int(float(argv[2]))

    oldTime = -1
    transaction = 0
    setup = False

    clustersSeen = set()

    for l in iFile:
        x = l.strip().split(',', 2)
        data = iDat(*x)
        currentTime = math.floor(int(float(data.time)) / int(seconds))

        # 1x setup
        if not setup:
            oldTime = currentTime
            setup = True

        # time to write out the old
        if currentTime != oldTime:
            transaction += 1
            outputSet(oFile, clustersSeen, transaction)
            clustersSeen.clear()

        clustersSeen.add(data.cluster)

        oldTime = currentTime

    # any leftovers needs to be written out
    if len(clustersSeen) > 0:
        outputSet(oFile, clustersSeen, transaction)

    iFile.close()
    oFile.close()

if __name__ == '__main__':
    main(sys.argv[1:])
