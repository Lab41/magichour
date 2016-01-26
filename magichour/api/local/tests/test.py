import time
from timeit import Timer
import cPickle as pickle

from magichour.api.local.preprocess import preprocess
from magichour.api.local.templates import templates, apply
from magichour.api.local.logging_util import get_logger

logger = get_logger(__name__)

transforms_file = "/Users/kylez/lab41/magichour/magichour/magichour/api/local/preprocess/simpleTrans"
log_file = "/Users/kylez/lab41/magichour/magichour/magichour/api/local/preprocess/tbird.log.500k"
# lines = preprocess.get_lines("/Users/kylez/lab41/magichour/magichour/magichour/api/local/preprocess/tbird.log.500k", 0, 10, skip_num_chars=22)

def test_preprocess():
    logger.debug("Reading transforms from file: %s" % transforms_file)
    transforms = preprocess.get_transforms(transforms_file)

    logger.debug("Reading log lines from file: %s" % log_file)
    lines = preprocess.get_lines(log_file, 0, 10, skip_num_chars=22)

    logger.debug("Transforming log lines...")
    transformed_lines = preprocess.get_transformed_lines(lines, transforms)

    logger.debug("Creating a list of transformed log lines...")
    start_time = time.time()
    transformed_lines = [line for line in transformed_lines]
    logger.debug("Elapsed time: %s" % (time.time() - start_time))
    logger.debug("# transformed lines: %s" % len(transformed_lines))
    return transformed_lines

def test_logcluster(transformed_lines):
    SUPPORT = 50

    logger.debug("Calling logcluster with support = %s" % SUPPORT)
    t = templates.logcluster(transformed_lines, logcluster_kwargs={"support": str(SUPPORT)})
    return t

def test_stringmatch(transformed_lines):
    t = templates.stringmatch(transformed_lines)
    return t


if __name__ == "__main__":
    DIVIDER = "="*20+"\n"
    transformed_lines_file = "transformed_lines.pickle"

    logger.debug("Step 1: preprocess")
    """
    transformed_lines = test_preprocess()
    logger.debug("Writing transformed_lines to file: %s" % transformed_lines_file)
    with open(transformed_lines_file, 'wb') as pf:
        pickle.dump(transformed_lines, pf)
    """
    logger.debug("Loading transformed_lines from file: %s" % transformed_lines_file)
    with open(transformed_lines_file, 'rb') as pf:
        transformed_lines = pickle.load(pf)
    
    logger.debug(DIVIDER)

    logger.debug("Step 2: template")
    t = test_logcluster(transformed_lines)
    
    logger.debug(DIVIDER)

    logger.debug("Step 3: apply templates")
    timed_templates = apply.apply_templates(t, transformed_lines)

    logger.debug(DIVIDER)
