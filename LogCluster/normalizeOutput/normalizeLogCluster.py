import re
import time
import datetime
import sys


def readLines(f):
    a = open(f, 'r')
    retval = a.readlines()
    a.close()
    return retval


# TODO make sure to come back and revisit this...
# TODO there are a ton of things which need to be escaped
def escapeCrap(l):

    escaped = re.escape(l)
    return escaped


# TODO this is absolutely known wrong way
def badWay(r1, r2):
    return (len(r2) - len(r1))


# Make sure that small get done before large
# TODO do the correct thing someday
'''
correct way:

For each pair of regexes r and s for languages L(r) and L(s)
  Find the corresponding Deterministic Finite Automata M(r) and M(s)   [1]
    Compute the cross-product machine M(r x s) and assign accepting states
       so that it computes L(r) - L(s)
    Use a DFS or BFS of the the M(r x s) transition table to see if any
       accepting state can be reached from the start state
    If no, you can eliminate s because L(s) is a subset of L(r).
    Reassign accepting states so that M(r x s) computes L(s) - L(r)
    Repeat the steps above to see if it's possible to eliminate r

'''
def rankMatches(m):

    retval = sorted(m, cmp=badWay)
    print retval
    return retval


def parseClusterLines(l):
    matches = list()
    for o in range(0, len(l), 3):
        m = l[o].lstrip().rstrip()
        fixedLine = escapeCrap(m)
        matches.append(findReplacement(fixedLine).lstrip().rstrip())

    print 'pre'
    for m in matches:
        print m

    matches = rankMatches(matches)

    print 'post'
    for m in matches:
        print m

    return matches


def main(argv):

    sys.stderr.write('reading patterns %s\n' % (argv[0]))
    sys.stderr.write('reading logLines %s\n' % (argv[1]))

    if len(argv) == 3:
        sys.stderr.write('writing %s\n' % (argv[2]))
        outDesc = open(argv[2],'w')
    else:
        sys.stderr.write('writing to stdout\n')

        outDesc = sys.stdout


    cPatternRaw = readLines(argv[0])
    regList = parseClusterLines(cPatternRaw)
    lines = readLines(argv[1])

    print
    for cluster, r in enumerate(regList):
        sys.stderr.write( 'cluster:%i , %s\n' %( cluster, r))
    print

    for l in lines:
        for cluster, search in enumerate(regList):
            if re.search(search, l):
                t = l[:19]
                ts = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
                outDesc.write( '%s,%i,%s\n' % (time.mktime(ts.timetuple()),
                                    cluster,
                                    l[20:].rstrip().strip()))
                break


def findReplacement(s):
    # pattern = r'\*\{(\d*).(\d*)\}'
    pattern = r'\\ \\\*\\\{(\d*)\\,(\d)\\}'
    matchObj = re.finditer(pattern, s, re.M | re.I)
    b = s

    if matchObj:
        for m in matchObj:

            newString = r'(:?\ \S+){%i,%i}' % (int(m.groups()[0]),
                                               int(m.groups()[1]))
            # the r is very important
            newFound =r'\\ \\\*\\\{%i\\,%i\\}' % (int(m.groups()[0]),
                                                  int(m.groups()[1]))
            b = re.sub(newFound, newString, b)
        return b
    return s

if __name__ == "__main__":
    main(sys.argv[1:])