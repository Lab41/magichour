from collections import Counter
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
    Xr = Counter(list(permutations(X.rstrip().split(), 2)))

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


def changePartition(C, X, G, i, jStar):

    G[makeHash(X)] = jStar
    Xr = Counter(list(permutations(X.rstrip().split(), 2)))

    for r, count in Xr:
        C[i][r] = C[i][r] - count
        if r not in C[jStar]:
            C[jStar][r] = 0

        C[jStar][r] = C[jStar][r] + count


def listSetEqual(C, Clast):
    for i, s in enumerate(C):
        if s != Clast[i]:
            return False
    return True


# D : log message set
# k : number of groups to partition
# returns: C: log message partition
def logSig_localSearch(D, k):

    C = randomSeeds(D, k)
    CLast = [set() for _ in range(k)]

    # Create a map G to store messages group index
    G = dict()

    # place each logline into a set
    # TODO see if this would be better to conserve memory
    # by making this a k way lookup

    for i, Ci in enumerate(C):
        for X in Ci:
            G[makeHash(X)] = i

# TODO should this be an energy measure instead of dict?
    while not listSetEqual(C, CLast):

        CLast.deepcopy(C)

        for Xj in D:
            i = G[makeHash(Xj)]
            jStar = argMaxPhiSimple(C, X, G)

            if i != jStar:
                changePartition(C, Xj, G, i, jStar)
            # endif
        # endfor
    # end while
    return C
