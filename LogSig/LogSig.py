from collections import Counter
from functools32 import lru_cache
from itertools import combinations
import hashlib
import sys
import time
import signal

# Signal handler updates GLOBAL to stop processing
globalStop = False


# stop processing if CTRL-C pressed
# GOOD
def signal_handler(signal, frame):

    global globalStop
    globalStop = True


# return a md5 string representation of input string
# TODO lookup faster hashes
@lru_cache()
def makeHash(s):

    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


# make a concatenation of a tuple
# GOOD
# can make multiple things alias to the same comparison..
# 'a','aaa','aa','aa','aaa','a' all map to 'aaaa'
@lru_cache()
def tuple2Str(a):

    return '%s%s' % a


# make a counter object from a string
# GOOD
@lru_cache()
def str2Counter(X):

    # set chosen to make membership of a tuple instead of count of tuple
    # Counter is to track the number of DOCUMENTS containing the tuple
    # not the count of the tuples in a DOCUMENT.
    return Counter(map(tuple2Str, set(combinations(X.rstrip().split(), 2))))


# calculate the best partition for X to be in
# using the cheat sum(p(r,Cdest))
# TODO update with results from email to paper authors
# TODO (global update, p(r,C) )
# @profile
def argMaxPhiSimple(C, X, G, denominator):
    numGroups = len(C)

    # see which group X should be in to maximize
    partition = G[makeHash(X)]

    retScore = 0.0
    retval = partition

    Xr = str2Counter(X)

    for partition in range(numGroups):

        currentScore = 0.0
        numerator = 0.0

        for r in Xr.iterkeys():
            numerator += C[partition].get(r, 0)

        currentScore += numerator * numerator
        # TODO make sure this is the correct way to calculate
        d = denominator.get(partition, 0.000000000001)
        d = d*d
        currentScore = numerator / d

        # keep tabs of who is winning
        if retScore < currentScore:
            retScore = currentScore
            retval = partition

    return retval


# store the data histograms
# in each parition
# GOOD
def randomSeeds(D, k, G):

    C = [Counter() for _ in range(k)]
    partition = 0
    for d in D:

        # assigning groups to a message
        G[makeHash(d)] = partition

        # Do things the Counter way
        C[partition].update(str2Counter(d))
        partition = (partition + 1) % k

    print 'UniqLogLines', len(G)
    return C


# move X from partition i to partition j
# GOOD
def updatePartition(CNext, X, GNext, i, j):

    GNext[makeHash(X)] = j

    # TODO would a binary version of this be sufficient?
    CNext[j].update(str2Counter(X))


# determine if array of dicts are equal
# GOOD
def partitionsNotEqual(C, CNext):

    for i in range(len(C)):
        if C[i] != CNext[i]:
            # print '!=', C[i]
            # print '!=', CNext[i]
            return True
    # print '=='
    return False


# D : log message set
# k : number of groups to partition
# returns: C: partitions
# GOOD
def logSig_localSearch(D, G, k, maxIter):

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
    while partitionsNotSame and (limit < maxIter) and not globalStop:
        start = time.time()

        for X in D:
            i = G[makeHash(X)]
            j = argMaxPhiSimple(C, X, G, denominator)
            updatePartition(CNext, X, GNext, i, j)
            # endif
        # endfor

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
    # end while
    print '\niterated %i times' % (limit)

    return C


# GOOD
def main(argv):

    totalS = time.time()

    print 'Attempting to open %s' % (argv[0])
    print 'k = %i' % int(argv[1])
    print 'maxIter = %i' % int(argv[2])

    a = open(argv[0], 'r')
    D = list()
    G = dict()

    readCount = 0
    for l in a.readlines():
        readCount += 1
        D.append(l.strip())

    a.close()

    print 'Read %i items' % readCount
    logSig_localSearch(D, G, int(argv[1]), int(argv[2]))
    totalE = time.time()

    outHist = Counter(G.itervalues())
    partitions = sorted(set(G.itervalues()))

    # print a histogram of partition sizes
    for p in partitions:
        print p, outHist[p]

    print 'total execution time %s (sec)' % (totalE - totalS)
    print 'Partition |    Logline'
    print '__________+__________________________________________'

    # print things in partition order at the expense of looping
    for p in partitions:
        for d in D:
            if p == G[makeHash(d)]:
                print ' %03i      | %s' % (G[makeHash(d)], d)


if __name__ == "__main__":
    # install the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    main(sys.argv[1:])
