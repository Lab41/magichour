import collections
from itertools import permutations
import hashlib


# http://rosettacode.org/wiki/Longest_common_subsequence#Dynamic_Programming_7


def LCS(X, S):

    lengths = [[0 for j in range(len(S)+1)] for i in range(len(X)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(X):
        for j, y in enumerate(S):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = \
                    max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = 0
    x, y = len(X), len(S)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert X[x-1] == S[y-1]
            result = result + 1
            x -= 1
            y -= 1
    return result


def match(X, S):

    # TODO check to make sure that S is an array
    return 2 * LCS(X, S) - len(S)


def potentialIncrease(D):

    # TODO fill in potential loss funciton
    return 4


def makeHash(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


def getWeight(C):

    retval = 0
    for r, count in C:
        retval = retval + count
    return retval


def argMaxPhiSimple(C, X, G):
    # calculate the potential of X moving from cluster i to cluster j
    # using the simplified form *sum(r e R(X), p(r,Cj)^2 -p(r,Ci)^2)
    # using the cheat sum(p(r,Cdest))
    numGroups = len(C)
    retScore = 0.0
    retval = 0.0

    # make the tuples
    Xr = collections.Counter(list(permutations(X.rstrip().split(), 2)))

    # see which group X should be in to maximize
    currentGroup = G[makeHash(X)]
    for nextGroup in range(numGroups):
        currentScore = 0.0

        # dont consider transition to same group
        if nextGroup == currentGroup:
            continue

        sum = 0.0
        for r in Xr:
            sum = sum + C[nextGroup].get(r)
        # TODO make sure this is the correct way to calculate
        sum = sum / getWeight(C[nextGroup])

    # keep tabs of who is winning
    if retScore < currentScore:
        retScore = currentScore
        retval = currentGroup

    return retval


def randomSeeds(D, k):
    C = [set() for _ in range(k)]
    counter = 0
    for d in D:
        counter = (counter + 1) % k
        # place log lines into sets
        C[counter].add(d)
    return C

    # TODO fill in the partition randomization funciton
    return dict()


def union(a, b):

    # TODO fillk in the partition union function
    return a


def changePartition(C, Xj, G, i, jStar):

    # TODO fill in the change partition function
    G[makeHash(Xj)] = jStar
    C[i].remove(Xj)
    C[jStar].append(Xj)


# D : log message set
# k : number of groups to partition
# returns: C: log message partition
def logSig_localSearch(D, k):

    C = randomSeeds(D, k)
    CLast = 0
    # Create a map G to store messages group index
    G = dict()

    for i, Ci in enumerate(C):
        for Xj in Ci:
            G[makeHash(Xj)] = i

# TODO should this be an energy measure instead of set?
    while C != CLast:
        CLast = C
        for Xj in D:
            i = G[Xj]
            jStar = potentialIncrease(D, C, Xj)
            if i != jStar:
                changePartition(C, Xj, G, i, jStar)
            # endif
        # endfor
    # end while
    return C
