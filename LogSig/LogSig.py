from collections import Counter
from functools32 import lru_cache
from itertools import combinations
import hashlib
import sys
import time


# return a md5 string representation of input string
# GOOD
@lru_cache()
def makeHash(s):

    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


# make a concatenation of a tuple
# GOOD
@lru_cache()
def tuple2Str(a):

    return '%s%s' % a


# make a counter object from a string
# GOOD
@lru_cache()
def str2Counter(X):

    return Counter(map(tuple2Str, list(combinations(X.rstrip().split(), 2))))


# calculate the best partition for X to be in
# using the cheat sum(p(r,Cdest))
# ????
# @profile
def argMaxPhiSimple(C, X, G):
    numGroups = len(C)

    # see which group X should be in to maximize
    partition = G[makeHash(X)]

    retScore = 0.0
    retval = partition

    Xr = str2Counter(X)

    for partition in range(numGroups):

        currentScore = 0.0
        numerator = 0.0

        #
        # denominator = sum(C[partition].values())
        denominator = len(C[partition])

        for r in Xr.iterkeys():
            numerator += C[partition].get(r, 0)

        # TODO make sure this is the correct way to calculate
        currentScore = numerator / (denominator + 0.00000000001)
        currentScore = currentScore * currentScore

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
            return True
    return False


# D : log message set
# k : number of groups to partition
# returns: C: partitions
def logSig_localSearch(D, G, k, maxIter):

    GNext = dict()

    CNext = [Counter() for _ in range(k)]
    C = randomSeeds(D, k, G)

    print "Starting Run\n"

    # TODO should this be an energy measure
    # instead of dict comp?

    limit = 0
    while partitionsNotEqual(C, CNext) and limit < maxIter:
        start = time.time()

        for X in D:
            i = G[makeHash(X)]
            j = argMaxPhiSimple(C, X, G)
            updatePartition(CNext, X, GNext, i, j)
            # endif
        # endfor

        limit = limit + 1
        finish = time.time()

        # TODO is this the corret thing?
        C = CNext
        G = GNext

        CNext = [Counter() for _ in range(k)]
        GNext = dict()

        print 'looping iteration %i time=%3.4f (sec)' % (limit, finish - start)
    # end while
    print '\niterated %i times' % (limit)
    return C


# GOOD
def main(argv):

    totalS = time.time()
    # a = open('testFiles/logFile', 'r')
    print 'Attempting to open %s' % (argv[0])
    print 'k = %i' % int(argv[1])
    print 'maxIter = %i' % int(argv[2])
    a = open(argv[0], 'r')
    D = list()
    G = dict()
    readCount = 0
    for l in a.readlines():
        # print 'reading', l.strip()
        readCount += 1
        D.append(l.strip())
        if readCount > 1000:
            break

    a.close()

    print 'Read %i items' % readCount
    logSig_localSearch(D, G, int(argv[1]), int(argv[2]))
    totalE = time.time()

    print 'total execution time %s (sec)' % (totalE - totalS)
    print 'Partition |    Logline'
    print '__________+__________________________________________'
    for d in D:
        print ' %03i      | %s' % (G[makeHash(d)], d)


if __name__ == "__main__":

    main(sys.argv[1:])
