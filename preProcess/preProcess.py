from collections import namedtuple
import datetime
import re
import sys
import time
import argparse
import gzip


TDI = namedtuple('TDI', ['start', 'stop', 'fmat'])

LogLine = namedtuple('LogLine', ['ts', 'text', 'processed',
                                 'dictionary', 'supportId'])

TransformLine = namedtuple('TransformLine', ['id', 'type', 'NAME', 'transform'])


def openFile(name, mode):
    if name.lower().endswith('.gz'):
        return gzip.open(name, mode+'b')
    else:
        return open(name, mode)


def makeTransformedLine(l, transforms):
    text = l.text.strip()
    replaceDict = dict()
    FLAGS = re.MULTILINE | re.DOTALL
    for t in transforms:
        if t.type == 'REPLACE':
            replaceList = re.findall(t.transform, text)
            if replaceList:
                replaceDict[t.NAME] = replaceList
            text = re.sub(t.transform, ' '+t.NAME+' ', text, 0, FLAGS)

        if t.type == 'REPLACELIST':
            print 'REPLACELIST not implemented yet'

    processed = ' '.join(text.split())
    retVal = LogLine(l.ts, l.text.lstrip().rstrip(),
                     processed.lstrip().rstrip(), replaceDict, None)

    return retVal


def dataset_iterator(fIn, numLines, tdi, transforms):
    '''
        Handle reading the data from file into a know form
    '''
    lines_read = 0
    while numLines == -1 or lines_read < numLines:
        lines_read += 1
        line = fIn.readline()
        if len(line) == 0:
            break
        else:
            try:
                t = datetime.datetime.strptime(line[tdi.start:tdi.stop],
                                               tdi.fmat)
                ts = time.mktime(t.timetuple())
                left = line[:tdi.start]
                right = line[tdi.stop:]
                rest = left+right
                lline = LogLine(ts, rest, None, None, None)
                processed = makeTransformedLine(lline, transforms)
                yield processed

                '''

                logtype = 1
                if logtype == 0:
                    # syslogway
                    t = datetime.datetime.strptime(line[:14], '%b %d %H:%M:%S')
                    t.replace(year=2015)
                    ts = time.mktime(t.timetuple())
                    rest = line[15:].strip()
                    processed = processString(rest)
                    yield LogLine(ts, rest,  processed)
                    success_full += 1
                if logtype == 1:
                    # apache weblog way
                    t = datetime.datetime.strptime(line[1:25],
                                                   '%a %b %d %H:%M:%S %Y')
                    ts = time.mktime(t.timetuple())
                    rest = line[26:].lstrip().strip()
                    processed = processString(rest)
                    yield LogLine(ts, rest,  processed)
                    success_full += 1
                '''

            except:
                pass


def main(argv):

    letters = """'format string'
%%a The day of the week, using the locale's weekday names; either the
   abbreviated or full name may be specified.
%%A Equivalent to %%a.
%%b The month, using the locale's month names; either the abbreviated or full
   name may be specified.
%%B Equivalent to %%b.
%%c Replaced by the locale's appropriate date and time representation.
%%C The century number [00,99]; leading zeros are permitted but not required.
%%d The day of the month [01,31]; leading zeros are permitted but not required.
%%D The date as %%m / %%d / %%y.
%%e Equivalent to %%d.
%%h Equivalent to %%b.
%%H The hour (24-hour clock) [00,23]; leading zeros are permitted
    but not required.
%%I The hour (12-hour clock) [01,12]; leading zeros are permitted
    but not required.
%%j The day number of the year [001,366]; leading zeros are permitted but not
   required.
%%m The month number [01,12]; leading zeros are permitted but not required.
%%M The minute [00,59]; leading zeros are permitted but not required.
%%n Any white space.
%%p The locale's equivalent of a.m or p.m.
%%r 12-hour clock time using the AM/PM notation if t_fmt_ampm is not an empty
    string in the LC_TIME portion of the current locale; in the POSIX locale,
    this shall be equivalent to %%I : %%M : %%S %%p.
%%R The time as %%H : %%M.
%%S The seconds [00,60]; leading zeros are permitted but not required.
%%t Any white  space.
%%T The time as %%H : %%M : %%S.
%%U The week number of the year (Sunday as the first day of the week) as a
   decimal number [00,53]; leading zeros are permitted but not required.
%%w The weekday as a decimal number [0,6], with 0 representing Sunday;
   leading zeros are permitted but not required.
%%W The week number of the year (Monday as the first day of the week) as a
   decimal number [00,53]; leading zeros are permitted but not required.
%%x The date, using the locale's date format.
%%X The time, using the locale's time format.
%%y The year within century. When a century is not otherwise specified, values
   in the range [69,99] shall refer to years 1969 to 1999 inclusive, and values
   in the range [00,68] shall refer to years 2000 to 2068 inclusive; leading
   zeros shall be permitted but shall not be required.
%%Y The 4 digit year
"""

    parser = argparse.ArgumentParser(description='reformat input',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', nargs=1, help='input file')
    parser.add_argument('-o', nargs=1, help='output file')
    parser.add_argument('--start', required=True,  nargs=1,
                        help='index date start')
    parser.add_argument('--stop', required=True, nargs=1, help='index date end')
    parser.add_argument('-f', required=True, nargs=1, help=letters)
    parser.add_argument('-t', required=True, nargs=1,
                        help='file of transforms to apply')
    parsedArgs = parser.parse_args(argv)

    if parsedArgs.i is not None:
        sys.stderr.write('reading %s\n' % (parsedArgs.i[0]))
        i = openFile(parsedArgs.i[0], 'r')
    else:
        i = sys.stdin
        sys.stderr.write('reading stdin\n')

    if parsedArgs.f is not None:
        sys.stderr.write('reading transforms from file %s\n' %
                         (parsedArgs.t[0]))
        t = openFile(parsedArgs.t[0], 'r')

    if parsedArgs.o is not None:
        sys.stderr.write('writing %s\n' % (parsedArgs.o[0]))
        o = openFile(parsedArgs.o[0], 'w')
    else:
        o = sys.stdout
        sys.stderr.write('writing stdout\n')

    start = int(parsedArgs.start[0])
    stop = int(parsedArgs.stop[0])
    fmat = str(parsedArgs.f[0])
    tdi = TDI(start, stop, fmat)
    transforms = list()

    for trans in t:
        if trans.lstrip()[0] == '#':
            continue
        else:
            ID, TYPE, NAME, TRANSFORM = trans.lstrip().rstrip().split(',', 3)
            transforms.append(TransformLine(ID, TYPE, NAME, r''+TRANSFORM))

    for logLine in dataset_iterator(i, -1, tdi, transforms):
        out = '%s %s\n' % (logLine.ts, logLine.processed)
        o.write(out)

    i.close()
    o.close()
    t.close()
if __name__ == "__main__":

    main(sys.argv[1:])
