import sys


def computeStays(left, right):
    retval = 0
    for r in right:
        retval += left and right
    return retval


def computeExits(left, right, inner):
    retval = right(inner) - (left and right(inner))
    return retval


def makeComparisons(left, right):
    catagories = range(len(left))
    for outer in catagories:
        outLine = list()
        for inner in catagories:
            work = 0
            if outer == inner:
                work = computeStays(left[outer], right)
            else:
                work = computeExits(left[outer], right, inner)
            outLine.append(work)


def main(argv):
    print 'main'

if __name__ == "__main__":
    main(sys.argv[1:])
