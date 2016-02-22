import gzip
import logging
import numpy as np
import sys
import time

from itertools import islice
from optparse import OptionParser

from sklearn.preprocessing import LabelEncoder, scale
from sklearn.cluster import KMeans

from kernel_kmeans import KernelKMeans
from ssk import ssk, transform


def main():
    parser = OptionParser()

    parser.add_option("-f", "--filename", dest="filename",
                      help="Log file to read")
    parser.add_option(
        "-n",
        "--num_clusters",
        dest="num_clusters",
        type=int,
        default=0,
        help="Number of clusters to create")
    parser.add_option(
        "-s",
        "--subsequence_length",
        dest="subsequence_length",
        type=int,
        default=2,
        help="Subsequence length")
    parser.add_option(
        "-d",
        "--decay_factor",
        dest="decay_factor",
        type=float,
        default=0.5,
        help="Decay factor used to penalize subsequence distance. Valid range: 0.0 to 1.0")
    parser.add_option(
        "-l",
        '--num_lines',
        dest='num_lines',
        type=int,
        default=-1,
        help="Number of lines to read from log file. Default: -1")

    parser.add_option(
        "--num_skipchars",
        dest="num_skipchars",
        type=int,
        default=0,
        help="Number of characters to skip at the beginning of each line. Default: 0")

    scheme_choices = ("word", "character")
    default_scheme = "character"
    parser.add_option(
        "--scheme",
        dest="scheme",
        type="choice",
        choices=scheme_choices,
        default=default_scheme,
        help="Scheme for constructing subsequences. Valid choices: %s. Default: %s" %
        (scheme_choices,
         default_scheme))

    parser.add_option(
        "--kernel",
        action="store_true",
        dest="kernel_kmeans",
        default=False,
        help="Flag for using KernelKMeans algorithm instead of KMeans.")
    parser.add_option(
        "--nystroem",
        dest="nystroem",
        type=int,
        default=-
        1,
        help="Number of features to construct for approximating the kernel using the Nystroem method. Default: -1 (do not approximate kernel)")
    parser.add_option(
        "--max_iterations",
        dest="max_iterations",
        type=int,
        default=1000,
        help="Maximum number of iterations for algorithm.")

    logging_choices = ("ERROR", "WARNING", "INFO", "DEBUG")
    default_logging = "INFO"
    parser.add_option(
        "--log_level",
        dest="log_level",
        type="choice",
        choices=logging_choices,
        default=default_logging,
        help="Logging level. Valid choices: %s. Default: %s" %
        (logging_choices,
         default_logging))

    (options, args) = parser.parse_args()

    level = logging.getLevelName(options.log_level)
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)

    logger.debug("Opening file (%s)." % options.filename)
    open_fn = gzip.open if options.filename.endswith(".gz") else open
    with open_fn(options.filename) as f:
        if options.num_lines == -1:
            logger.debug("Reading entire file.")
            lines = f.readlines()
        else:
            logger.debug("Reading %s lines." % options.num_lines)
            lines = list(islice(f, options.num_lines))

    kmeans = None
    lines_w_times = lines
    if options.num_skipchars:
        logger.debug(
            "Skipping the first %s characters in each line (timestamp)." %
            options.num_skipchars)
        lines = [line[options.num_skipchars:] for line in lines]

    # TODO: offer minibatch k-means as a choice
    if options.kernel_kmeans:
        logger.debug("Kernel K-Means Clustering selected.")
        lb = LabelEncoder()
        l = lb.fit_transform(np.array(lines)).reshape(-1, 1)
        kmeans = KernelKMeans(
            n_clusters=options.num_clusters,
            max_iter=options.max_iterations,
            kernel=ssk,
            kernel_params={
                "label_encoder": lb},
            nystroem=options.nystroem)
        # Unlike KMeans from sklearn, KernelKMeans only runs once. Users should run the algorithms multiple times and
        # select the clustering that minimizes the inertia (within-cluster sum
        # of squared criterion).
        kmeans.fit(l)
    else:
        logger.debug("K-Means Clustering selected.")
        logger.debug("Doing subsequence transformation...")
        start_time = time.time()
        l = transform(
            lines,
            options.decay_factor,
            options.subsequence_length,
            options.scheme)
        l = scale(l)
        logger.debug("Duration: %s" % (time.time() - start_time))
        kmeans = KMeans(
            n_clusters=options.num_clusters,
            max_iter=options.max_iterations)
        kmeans.fit(l)

    # ============

    d = {}
    # May need to change this section depending on how you want to output the
    # log file.
    for group, s in zip(kmeans.labels_, lines_w_times):
        epoch = timestamp = s[:options.num_skipchars]
        #epoch = int(time.mktime(time.strptime(timestamp.strip()[1:-1], "%a %b %d %H:%M:%S %Y")))
        epoch = int(
            time.mktime(
                time.strptime(
                    timestamp.strip(),
                    "%Y-%m-%d %H:%M:%S")))
        msg = s[options.num_skipchars:]
        l = d.get(group, [])
        l.append((epoch, group, msg))
        d[group] = l
        # print "%s,%s,%s" % (epoch, group, msg.strip())

    # Pretty print clusters.
    for x in d.keys():
        for epoch, group, msg in d[x]:
            print "%s,%s,%s" % (epoch, group, msg.strip())
        # print "--------------------"

if __name__ == "__main__":
    main()
