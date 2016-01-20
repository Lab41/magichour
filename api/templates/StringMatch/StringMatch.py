from __future__ import division
import sys
from optparse import OptionParser
from itertools import islice
import gzip
from collections import defaultdict
from math import floor, sqrt, log10
import datetime

from utils import *
from cluster import Cluster, LogLine
from leaf import Leaf


def get_clusters(dataset_iterator, batch_size, skip_count, threshold, MIN_SAMPLES_FOR_SPLIT):
    line_count = 0
    clusters = []
    for line in dataset_iterator:
        line_split = line.msg.split()
        if len(line_split) > skip_count:
            has_matched = False
            for i in range(len(clusters)):
                if clusters[i].check_for_match(line_split, threshold, skip_count):
                    clusters[i].add_to_leaf(line, threshold, skip_count)
                    has_matched = True

            if not has_matched:
                clusters.append(Cluster(Leaf(line)))    # Create a new cluster

        line_count += 1

        if line_count > batch_size:
            # Split leafs that are too large
            for i in range(len(clusters)):
                if clusters[i].get_num_lines() > MIN_SAMPLES_FOR_SPLIT:
                    clusters[i].split_leaf(MIN_SAMPLES_FOR_SPLIT, skip_count, min_word_pos_entropy=.0001, min_percent=.1)

            line_count = 0
    return clusters


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

    def dataset_iterator(fIn, num_lines=options.num_lines):
        lines_read = 0
        success_full = 0
        while num_lines== -1 or lines_read < num_lines:
            lines_read += 1
            line = fIn.readline()
            if len(line) == 0:
                break
            else:
                try:
                    ts = datetime.datetime.strptime(line[:14], '%b %d %H:%M:%S')
                    yield LogLine(ts.replace(year=2015), line.strip()[:15])
                    success_full += 1
                except:
                    pass
                    #raise


    clusters = get_clusters(dataset_iterator(fIn), num_msgs, skip_count, threshold, MIN_SAMPLES_FOR_SPLIT)

    index = 0
    for cluster in clusters:
        index = cluster.print_groups(index)

if __name__ == "__main__":
    main()
