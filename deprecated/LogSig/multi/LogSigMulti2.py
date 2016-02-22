from collections import Counter
from itertools import combinations
from collections import namedtuple
from functools import partial
import multiprocessing
import datetime
import hashlib
import sys
import time
import signal
import gzip

'''
name some intermediate data structures
'''
LogLine = namedtuple('LogLine', ['ts', 'text'])
DataRecord = namedtuple('DataRecord', ['line', 'md5hash', 'stats'])

# Signal handler updates GLOBAL to stop processing
globalStop = False


def openFile(name, mode):
    if name.lower().endswith('.gz'):
        return gzip.open(name, mode + 'b')
    else:
        return open(name, mode)


# TODO make sure that this is correct

def makeEdges(m, i):

    retval = []
    ranOnce = False
    d = 0
    c = 0
    while c < m - 1 - i:
        ranOnce = True
        d = c
        c = c + i
        retval.append((d, c))
    if (m - d) > 0:
        retval.append((c, m))

    if not ranOnce:
        retval.append((0, m))

    return retval


def distribWork(C, G, denominator, D, workBounds):
    start, finish = workBounds
    CNext = [Counter() for _ in range(len(C))]
    GNext = dict()

    for i in range(start, finish):
        j = argMaxPhiSimple(C, D[i], G, denominator)
        GNext[D[i].md5hash] = j
        CNext[j].update(D[i].stats)
    return (CNext, GNext)


# GOOD
def signal_handler(signal, frame):
    '''
         stop processing if CTRL-C pressed
    '''

    global globalStop
    globalStop = True


# TODO lookup faster hashes
def makeHash(s):
    '''
        make a md5 string rep of an input string
    '''

    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


# GOOD
def tuple2Str(a):
    '''
         make a concatenation of a tuple
         can make multiple things alias to the same comparison..
         'a','aaa','aa','aa','aaa','a' all map to 'aaaa'
    '''

    return '%s%s' % a


# GOOD
def str2Counter(X):
    '''
        make a counter object from a string
        set chosen to make membership of a tuple instead of count of tuple
        Counter is to track the number of DOCUMENTS containing the tuple
        not the count of the tuples in a DOCUMENT.
    '''
    return Counter(map(tuple2Str, set(combinations(X.rstrip().split(), 2))))


# TODO update with results from email to paper authors
# @profile
def argMaxPhiSimple(C, X, G, denominator):
    '''
        calculate the best partition for X to be part of
        return the number of the partition to caller
    '''
    numGroups = len(C)

    # see which group X should be in to maximize
    partition = G[X.md5hash]

    retScore = 0.0
    retval = partition

    Xr = X.stats

    for partition in range(numGroups):

        currentScore = 0.0
        numerator = 0.0

        for r in Xr.iterkeys():
            numerator += C[partition].get(r, 0)

        currentScore += numerator * numerator

        # TODO make sure this is the correct way to calculate
        # currentScore should be Sum(p(r,C)^2)

        d = denominator.get(partition, 0.000000000001)
        d = d * d
        currentScore = numerator / d

        # keep tabs of who is winning
        if retScore < currentScore:
            retScore = currentScore
            retval = partition

    return retval


# GOOD
def randomSeeds(D, k, G):
    '''
        store the data histograms
        in each parition
    '''

    C = [Counter() for _ in range(k)]
    partition = 0
    for d in D:

        # assigning groups to a message
        G[d.md5hash] = partition

        # Do things the Counter way
        C[partition].update(d.stats)
        partition = (partition + 1) % k

    print 'UniqLogLines', len(G)
    return C


# GOOD
def updatePartition(CNext, X, GNext, j):
    '''
        update CNext with statistics from X
        update GNext with which group X belongs
    '''

    GNext[X.md5hash] = j

    # TODO would a binary version of this be sufficient?
    CNext[j].update(X.stats)


# GOOD
def partitionsNotEqual(C, CNext):
    '''
        determine if array of dicts are equal
    '''

    for i in range(len(C)):
        if C[i] != CNext[i]:
            return True
    return False


# GOOD
def logSig_localSearch(D, G, k, maxIter):
    '''
        D : log message set
        k : number of groups to partition
        returns: C: partitions
    '''

    global globalStop

    GNext = dict()

    CNext = [Counter() for _ in range(k)]
    C = randomSeeds(D, k, G)
    denominator = Counter(G.itervalues())
    print "Starting Run\n"

    # TODO should this be an energy measure
    # instead of dict comp?

    limit = 0
    partitionsNotSame = True

    eL = makeEdges(len(D), 500)

    while partitionsNotSame and (limit < maxIter) and not globalStop:
        start = time.time()

        pool = multiprocessing.Pool()
        func = partial(distribWork, C, G, denominator, D)
        distribOut = pool.map(func, eL)
        pool.close()
        pool.join()

        for o in distribOut:
            tempCNext, tempGNext = o
            GNext.update(tempGNext)
            # for key, value in tempGNext.iteritems():
            #     GNext[key] = value
            for c in range(len(CNext)):
                CNext[c].update(tempCNext[c])

        print 'sanity next %i current %i' % (len(GNext), len(G))

        limit += 1
        finish = time.time()

        # make sure to stop when partitions stable
        partitionsNotSame = partitionsNotEqual(C, CNext)

        # TODO is this the corret thing?
        C = CNext

        # update for passing back
        G.clear()
        G.update(GNext)

        CNext = [Counter() for _ in range(k)]
        GNext = dict()

        denominator = Counter(G.itervalues())

        print 'looping iteration %i time=%3.4f (sec)' % (limit, finish - start)
        sys.stdout.flush()
    # end while
    print '\niterated %i times' % (limit)

    return C


# GOOD
def dataset_iterator(fIn, num_lines):
    '''
        Handle reading the data from file into a know form
    '''
    lines_read = 0
    success_full = 0
    while num_lines == -1 or lines_read < num_lines:
        lines_read += 1
        line = fIn.readline()
        if len(line) == 0:
            break
        else:
            try:
                ts = datetime.datetime.strptime(line[:14], '%b %d %H:%M:%S')
                yield LogLine(ts.replace(year=2015), line[15:].strip())
                success_full += 1
            except:
                pass


# GOOD
def main(argv):

    totalS = time.time()

    print 'Attempting to open %s' % (argv[0])
    print 'k = %i' % int(argv[1])
    print 'maxIter = %i' % int(argv[2])

    a = openFile(argv[0], 'r')
    D = list()
    G = dict()

    readCount = 0

    for r in dataset_iterator(a, -1):
        h = makeHash(r.text)
        s = str2Counter(r.text)
        D.append(DataRecord(r, h, s))
        readCount += 1

    a.close()

    print 'Read %i items' % readCount
    logSig_localSearch(D, G, int(argv[1]), int(argv[2]))
    totalE = time.time()

    outHist = Counter(G.itervalues())
    partitions = sorted(set(G.itervalues()))

    # print a histogram of partition sizes
    print 'cluster|number'
    for p in partitions:
        print '%4i|%4i' % (p, outHist[p])

    print 'total execution time %s (sec)\n' % (totalE - totalS)

    outSet = set()
    outDict = dict()

    for item in G.itervalues():
        outSet.add(item)

    for index, item in enumerate(outSet):
        outDict[item] = index

    # print things in partition order at the expense of looping
    for p in partitions:
        for d in D:
            if p == G[d.md5hash]:
                # print ' %03i      | %s' % (G[d.md5hash], d.line.text)
                print '%s,%s,%s' % (time.mktime(d.line.ts.timetuple()),
                                    outDict[G[d.md5hash]],
                                    d.line.text)

if __name__ == "__main__":
    # install the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    main(sys.argv[1:])
