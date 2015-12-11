from collections import namedtuple
import datetime
import re
import sys
import time
import argparse


LogLine = namedtuple('LogLine', ['ts', 'text', 'processed'])
TDI = namedtuple('TDI', ['start', 'stop', 'fmat'])


def processString(inText):
    FLAGS = re.MULTILINE | re.DOTALL
    URL = ' URL '
    FILEPATH = ' FILEPATH '
    IPADDR = ' IPADDR '
    FILEANDLINE = ' FILEANDLINE '
    DATE = ' DATE '
    TIME = ' TIME '
    SILENTREMOVE = ''
    SPACE = ' '
    AFILE = ' AFILE '
    LEVEL = ' LEVEL '
    INT = ' INT '

    badchars = [r'\[', r'\]', r'\(', r'\)', r'{', r'}', r':', r',', r'-']
    silentchars = [r'\"', r'\.', r'\'', r'\`', r'!']
    text = ""+inText.lower()

    text = re.sub(r'(?:\d{2}:\d{2}:\d{2},\d{3})', TIME, text, FLAGS)
    text = re.sub(r'(?:\d{4}-\d{2}-\d{2})', DATE, text, FLAGS)
    text = re.sub(r'(\w+\.)+(\w+):\d{1,10}', FILEANDLINE, text, FLAGS)
    text = re.sub(r'https?:\/\/\S+', URL, text, FLAGS)
    text = re.sub(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)' +
                  r'{3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
                  IPADDR, text, FLAGS)
    text = re.sub(r'(\S+)\/([^\/]?)(?:\S+)', FILEPATH, text, FLAGS)
    text = re.sub(r'(?:(\w+\.)+\w{1,3})', AFILE, text, FLAGS)
    text = re.sub(r'debug|error|fatal|info|trace|trace_int' +
                  r'|warn|alert|error|crit', LEVEL, text, FLAGS)

    text = re.sub(r'(?:\d+)', INT, text, FLAGS)

    for c in badchars:
        text = re.sub(c, SPACE, text, FLAGS)

    for c in silentchars:
            text = re.sub(c, SILENTREMOVE, text, FLAGS)

    text = re.sub(r'\s+', ' ', text, FLAGS)

    return text.lstrip().rstrip()


def dataset_iterator(fIn, num_lines, tdi):
    '''
        Handle reading the data from file into a know form
    '''
    lines_read = 0
    while num_lines == -1 or lines_read < num_lines:
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
                processed = processString(rest)
                yield LogLine(ts, rest,  processed)

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
"""

    parser = argparse.ArgumentParser(description='reformat input',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', required=True, nargs=1, help='input file')
    parser.add_argument('-o', nargs=1, help='output file')
    parser.add_argument('--start', required=True,  nargs=1,
                        help='index date start')
    parser.add_argument('--stop', required=True, nargs=1, help='index date end')
    parser.add_argument('-f', required=True, nargs=1, help=letters )
    parsedArgs = parser.parse_args(argv)


    print 'reading %s' % (parsedArgs.i[0])
    a = open(str(parsedArgs.i[0]), 'r')
    if parsedArgs.o != None:
        print 'writing %s' % (parsedArgs.o[0])
        b = open(str(parsedArgs.o[0]), 'w')
    else:
        b = sys.stdout
        print 'writing stdout'

    start = int(parsedArgs.start[0])
    stop = int(parsedArgs.stop[0])
    fmat = str(parsedArgs.f[0])
    tdi = TDI(start, stop, fmat)

    for logLine in dataset_iterator(a, -1, tdi):
        out = '%s %s\n' % (logLine.ts, logLine.processed)
        b.write(out)

    a.close()
    b.close()

if __name__ == "__main__":

    main(sys.argv[1:])
