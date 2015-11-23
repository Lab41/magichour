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


def crazyFunction(D):

    # TODO fill in potential loss funciton
    return 4


def randomSeeds(D, k):

    # TODO fill in the partition randomization funciton
    return dict()


def union(a, b):

    # TODO fillk in the partition union function
    return a


def changePartition(C, G, Xj, i, jStar):

    # TODO fill in the change partition function
    G[Xj] = jStar
    C[i].remove(Xj)
    C[jStar].append(Xj)


# D : log message set
# k : number of groups to partition
# returns: C: log message partition
def logSig_localSearch(D, k):

    C = randomSeeds(D, k)
    CPrime = 0
    # Create a map G to store messages group index
    G = dict()

    for i, Ci in enumerate(C):
        for Xj in Ci:
            G[Xj] = i

    while C != CPrime:
        CPrime = C
        for Xj in D:
            i = G[Xj]
            jStar = crazyFunction(D)
            if i != jStar:
                changePartition(C, G, Xj, i, jStar)
#           endif
#       endfor
#   end while
    return C
