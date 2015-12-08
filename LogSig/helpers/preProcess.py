from collections import namedtuple
import datetime
import re
import sys


LogLine = namedtuple('LogLine', ['ts', 'text', 'processed'])


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
    text = re.sub(r'(?:\w+(\.?)+:\d+)', FILEANDLINE, text, FLAGS)
    text = re.sub(r'https?:\/\/\S+', URL, text, FLAGS)
    text = re.sub(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', IPADDR, text, FLAGS)
    text = re.sub(r'(\S+)\/([^\/]?)(?:\S+)', FILEPATH, text, FLAGS)
    text = re.sub(r'(?:(\w+\.)+\w{1,3})', AFILE, text, FLAGS)
    text = re.sub(r'alert|error|crit', LEVEL, text, FLAGS)

    text = re.sub(r'(?:\d+)', INT, text, FLAGS)

    for c in badchars:
        text = re.sub(c, SPACE, text, FLAGS)

    for c in silentchars:
            text = re.sub(c, SILENTREMOVE, text, FLAGS)

    text = re.sub(r'\s+', ' ', text, FLAGS)

    print inText
    print text

    return text.lstrip().rstrip()


def dataset_iterator(fIn, num_lines):
    '''
        Handle reading the data from file into a know form
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
                    ts = datetime.datetime.strptime(line[:14], '%b %d %H:%M:%S')
                    rest = line[15:].strip()
                    processed = processString(rest)
                    yield LogLine(ts.replace(year=2015), rest,  processed)
                    success_full += 1
                if logtype == 1:
                    # apache weblog way
                    ts = datetime.datetime.strptime(line[1:25],
                                                    '%a %b %d %H:%M:%S %Y')
                    rest = line[27:].strip()
                    processed = processString(rest)
                    yield LogLine(ts, rest,  processed)
                    success_full += 1

            except:
                pass


def main(argv):
    print 'reading %s, writing %s' % (argv[0], argv[1])
    a = open(argv[0], 'r')
    b = open(argv[1], 'w')

    for logLine in dataset_iterator(a, -1):
        out = '%s %s\n' % (logLine.ts, logLine.processed)
        b.write(out)

    a.close()
    b.close()

if __name__ == "__main__":

    main(sys.argv[1:])
