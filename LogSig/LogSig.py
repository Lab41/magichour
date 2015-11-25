from collections import Counter
from functools32 import lru_cache
from itertools import combinations
import hashlib
import copy
import sys
import time


# return a md5 string representation of input string
@lru_cache()
def makeHash(s):

    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


@lru_cache()
def makeStr(a):

    return '%s%s' % a


@lru_cache()
def makeCounter(X):

    # return Counter(list(combinations(X.rstrip().split(), 2)))
    return Counter(map(makeStr, list(combinations(X.rstrip().split(), 2))))


# calculate the magnitude of a partition
def getMagnitude(C):
    retval = 1
    for key, count in C.iteritems():
        retval = retval + int(count)
    return retval


# calculate the best partition for X to be in
# using the cheat sum(p(r,Cdest))
def argMaxPhiSimple(C, X, G):
    numGroups = len(C)

    # see which group X should be in to maximize
    currentGroup = G[makeHash(X)]

    retScore = 0.0
    retval = currentGroup

    # make the tuples
    # Xr = Counter(list(combinations(X.rstrip().split(), 2)))
    Xr = makeCounter(X)

    for nextGroup in range(numGroups):
        # print 'Grouploop'
        # dont consider transition to same group
        if nextGroup == currentGroup:
            continue

        currentScore = 0.0
        # TODO make sure that this is not 0 in a better way
        denominator = sum(C[nextGroup].values())  # + 0.00000000001

        numerator = 0.0
        for r, count in Xr.iteritems():
            if r in C[nextGroup]:
                numerator = numerator + C[nextGroup].get(r)

        # TODO make sure this is the correct way to calculate
        currentScore = numerator / denominator

        # print 'ng', nextGroup, 'cs', currentScore
        # keep tabs of who is winning
        if retScore < currentScore:
            retScore = currentScore
            retval = nextGroup

    return retval


# store the data histograms
# in each parition
def randomSeeds(D, k, G):

    C = [Counter() for _ in range(k)]
    partition = 0
    for d in D:
        # make histograms of loglines
        # TODO make sure that is is correct way of
        # assigning groups to a message
        G[makeHash(d)] = partition
        # Xr = Counter(list(combinations(d.strip().split(), 2)))
        Xr = makeCounter(d)

        # Do things the Counter way
        C[partition].update(Xr)
        partition = (partition + 1) % k
    return C


# move X from partition i to partition j
def changePartition(C, X, G, i, j):

    # TODO would a binary version of this be sufficient?

    G[makeHash(X)] = j

    # TODO memorization
    # Xr = Counter(list(combinations(X.rstrip().split(), 2)))
    Xr = makeCounter(X)

    # do things the Counter way
    # C[i] = C[i] - Xr

    # fastar than the counter way..
    for key, count in Xr.iteritems():
        if key in C[i]:
            temp = C[i][key] - count
            if temp <= 0:
                C[i].pop(key)
            else:
                C[i][key] = temp

    C[j].update(Xr)


# D : log message set
# k : number of groups to partition
# returns: C: partitions
def logSig_localSearch(D, G, k):

    # Create a map G to store messages group index
    # G = dict()

    CLast = [Counter() for _ in range(k)]
    C = randomSeeds(D, k, G)

    # print 'C', len(C)
    # print 'CLast', len(CLast)

    # TODO should this be an energy measure
    # instead of dict comp?

    limit = 0
    # while not listDictEqual(C, CLast) and limit < 1000:
    print "Starting Run\n"
    while C != CLast and limit < 10000:
        start = time.time()
        # TODO is this the best way?
        CLast = copy.deepcopy(C)

        for X in D:
            # print 'x', X
            i = G[makeHash(X)]
            jStar = argMaxPhiSimple(C, X, G)
            # print 'i = %i, jStar= %i' % (i, jStar)
            if i != jStar:
                # print 'moving %s from %i to %i' % (X, i, jStar)
                changePartition(C, X, G, i, jStar)
            # endif
        # endfor
        limit = limit + 1
        finish = time.time()
        print 'looping iteration %i time=%3.4f (sec)' % (limit, finish - start)
    # end while
    print '\niterated %i times' % (limit)
    return C


def main(argv):

    totalS = time.time()
    # a = open('testFiles/logFile', 'r')
    print 'Attempting to open %s' % (argv[0])
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
    logSig_localSearch(D, G, int(argv[1]))
    totalE = time.time()

    print 'total execution time %s (sec)' % (totalE - totalS)
    print 'Partition |    Logline'
    print '__________+__________________________________________'
    for d in D:
        print ' %03i      | %s' % (G[makeHash(d)], d)


if __name__ == "__main__":

    main(sys.argv[1:])
