from collections import Counter
from itertools import combinations
from collections import namedtuple
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


# GOOD
def signal_handler(signal, frame):

    '''
         stop processing if CTRL-C pressed
         Args:
             signal
             frame
         Returns:
             None
         Globals:
             globalStop: loop guard
    '''

    global globalStop
    globalStop = True


# TODO lookup faster hashes
def makeHash(s):
    '''
        make a md5 string rep of an input string
        Args:
            s(string): input string
        Returns:
            stringDigest(string): string representation of the hex digest

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

         Args:
             a(tuple): tuple of strings
         Returns:
             concatTuple(string): concatenation string
    '''

    return '%s%s' % a


# GOOD
def str2Counter(X):
    '''
        make a counter object from a string
        set chosen to make membership of a tuple instead of count of tuple
        Counter is to track the number of DOCUMENTS containing the tuple
        not the count of the tuples in a DOCUMENT.

        Args:
            X(string): string to tokenize and count
        Returns:
            stats(collections.Counter)
    '''
    return Counter(map(tuple2Str, set(combinations(X.rstrip().split(), 2))))


# TODO update with results from email to paper authors
# @profile
def argMaxPhiSimple(C, X, G, denominator):
    '''
        calculate the best partition for X to be part of
        return the number of the partition to caller

        Args:
            C(): current mapping of loglines to partitions
            X(dataRecord): processed logline being evaluated
            G(dict): longline to partition mapping
            denominator(dict): parition to float mapping.  The lookup
                               is used to keep from repeatedly calculating
                               the denominator in a calculation

        Returns:
            idealPartition(int): X's partition for the next
                                 iteration of the algorithm
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
        d = d*d
        currentScore = numerator / d

        # keep tabs of who is winning
        if retScore < currentScore:
            retScore = currentScore
            retval = partition

    return retval


# GOOD
def randomSeeds(D, k, G):
    '''
        initial assignment of loglines to partitions

        Args:
            D(list(DataRecords)):
            k(int): number of partitions to make
            G(dict): logline to partition mapping

        Returns:
            C(list(Counters)):  Initial partition assignments for all
                                the log lines
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

        Args:
            CNext(list(Counters)):
            X(DataRecord): namedTuple about a single logline
            GNext(dict): logline to parition mapping
            j(int)

        Returns:
            None
    '''

    # update the next locaction for X
    GNext[X.md5hash] = j

    # TODO would a binary version of this be sufficient?
    CNext[j].update(X.stats)


# GOOD
def partitionsNotEqual(C, CNext):
    '''
        determine if array of counters are equal

        Args:
            C(list(Counter)) : current interation view of partition membership
            CNext(list(Counter)): next iteration view of partition membership

        Returns:
            retval(boolean): True -> same
                             False -> different
    '''

    for i in range(len(C)):
        if C[i] != CNext[i]:
            return True
    return False


# GOOD
def logSig_localSearch(D, G, k, maxIter):
    '''
        Perform the logsig_localsearch algorithm described in paper:
        LogSig: Geneerating Ssytem Events from Raw Textual Logs

        Args:
            D(list(DataRecord)): list of DataRecords storing the loglines
            G(dict): mapping between message and parition
            k(int) : number of groups to partition
            maxIter(int): maximum interations to perform before giving up
                          on convergence
        Returns:
            C(list(Counters)): partition statisitics
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
    while partitionsNotSame and (limit < maxIter) and not globalStop:
        start = time.time()

        for X in D:
            j = argMaxPhiSimple(C, X, G, denominator)
            updatePartition(CNext, X, GNext, j)
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
        sys.stdout.flush()
    # end while
    print '\niterated %i times' % (limit)

    return C


# GOOD
def dataset_iterator(fIn, num_lines):
    '''
        Handle reading the data from file into a know form

        Args:
            fIn(file): input file handle to read from
            num_lines(int): number of lines to read at once
        Returns:
            retVal(LogLine): a parsed logline
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
                logtype = 1
                if logtype == 0:
                    # syslogway
                    t = datetime.datetime.strptime(line[:14], '%b %d %H:%M:%S')
                    t.replace(year=2015)
                    ts = time.mktime(t.timetuple())
                    yield LogLine(ts, line[15:].strip())
                    success_full += 1
                if logtype == 1:
                    # apache weblog way
                    t = datetime.datetime.strptime(line[1:25],
                                                   '%a %b %d %H:%M:%S %Y')
                    ts = time.mktime(t.timetuple())
                    yield LogLine(ts, line[27:].strip())
                    success_full += 1
            except:
                pass


def openFile(name, mode):
    '''
        wrapps the open call to handle gzipped input/output

        Args:
            name(string): name of file to open, if the filename ends in a
                          '.gz' extension then treat file as a gzip
            mode(string): mode to open the file as
        Returns:
            retval(file): filehandle
    '''

    if name.lower().endswith('.gz'):
        return gzip.open(name, mode+'b')
    else:
        return open(name, mode)


# GOOD
def main(argv):
    '''
        main program calculating the LogSig

        Args:
            argv(list(string)): arguments of main program

        Returns:
            None
    '''

    totalS = time.time()

    out = None

    print 'Attempting to open %s' % (argv[0])
    print 'k = %i' % int(argv[1])
    print 'maxIter = %i' % int(argv[2])
    if len(argv) > 3:
        print 'ClusterOutputFile = %s' % argv[3]
        out = openFile(argv[3], 'w')
    else:
        out = sys.stdout

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
                outLine = '%s,%s,%s\n' % (d.line.ts,
                                          outDict[G[d.md5hash]],
                                          d.line.text)
                out.write(outLine)
    out.close()

if __name__ == "__main__":
    # install the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    main(sys.argv[1:])
