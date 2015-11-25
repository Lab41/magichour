from __future__ import division
import sys
from optparse import OptionParser
from itertools import islice
import gzip
from collections import defaultdict
from math import floor, sqrt, log10

from utils import *
from cluster import Cluster
from leaf import Leaf




def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="Log file to read")
    parser.add_option("--skip_count", dest='skip_count', type=int, default=0,
                      help="Number of tokens to skip at start of the line")
    parser.add_option("--threshold", dest='threshold', type=float, default=0.75,
                      help="Threshold for cosine similarity")
    parser.add_option("-l", '--num_lines', dest='num_lines', type=int, default=-1,
                      help="Number of lines to read from log file (default:-1 Whole file)")
    parser.add_option('--min_samples_for_split', dest='min_samples_for_split', type=int, default=25)
    parser.add_option('--batch_size', dest='batch_size', type=int, default=5000)

    (options, args) = parser.parse_args()

    num_msgs = options.batch_size
    skip_count = options.skip_count
    threshold = options.threshold
    MIN_SAMPLES_FOR_SPLIT = options.min_samples_for_split

    if options.filename.endswith('.gz'):
        fIn = gzip.open(options.filename)
    else:
        fIn = open(options.filename)
    #fIn = open('/var/log/system.log')#gzip.open(fname)#.readlines()[:num_msgs]


    total_lines_read = 0
    time_to_stop = False
    clusters = []
    prev_num_clusters = -1
    while total_lines_read < options.num_lines or (options.num_lines == -1 and not time_to_stop):
        print total_lines_read
        # Read in log lines
        lines = [line.strip() for line in islice(fIn, num_msgs)]
        print 'Done Reading'

        total_lines_read += len(lines)
        if len(lines) != num_msgs: # We got to the end of the file
            print 'Stopping', len(lines), num_msgs
            time_to_stop = True

        # Process a set of log lines
        for line in lines:
            line_split = line.split()
            if len(line_split) > skip_count:
                has_matched = False
                for i in range(len(clusters)):
                    if clusters[i].check_for_match(line_split, threshold, skip_count):
                        clusters[i].add_to_leaf(line, threshold, skip_count)
                        has_matched = True

                if not has_matched:
                    clusters.append(Cluster(Leaf(line)))    # Create a new cluster

        print 'Done Processing, starting check for splits '
        if prev_num_clusters != len(clusters):
            print "Currently have %d clusters"%len(clusters)
            prev_num_clusters = len(clusters)

        # Split leafs that are too large
        for i in range(len(clusters)):
            if clusters[i].get_num_lines() > MIN_SAMPLES_FOR_SPLIT:
                clusters[i].split_leaf(MIN_SAMPLES_FOR_SPLIT, skip_count, min_word_pos_entropy=.0001, min_percent=.1)
    for cluster in clusters:
        cluster.print_template_lines(0)

if __name__ == "__main__":
    main()