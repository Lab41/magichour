import time
import cPickle as pickle
import multiprocessing

from magichour.api.local.preprocess import preprocess
from magichour.api.local.templates import templates, apply
from magichour.api.local.windows import windows
from magichour.api.local.events import events
from magichour.api.local.logging_util import get_logger

logger = get_logger(__name__)

transforms_file = "/Users/kylez/lab41/magichour/magichour/magichour/api/local/preprocess/simpleTrans"
log_file = "/Users/kylez/lab41/magichour/magichour/magichour/api/local/preprocess/tbird.log.500k"
# lines = preprocess.get_lines("/Users/kylez/lab41/magichour/magichour/magichour/api/local/preprocess/tbird.log.500k", 0, 10, skip_num_chars=22)

def test_preprocess():
    logger.info("Reading transforms from file: %s" % transforms_file)
    transforms = preprocess.get_transforms(transforms_file)

    logger.info("Reading log lines from file: %s" % log_file)
    lines = preprocess.get_lines(log_file, 0, 10, skip_num_chars=22)

    logger.info("Transforming log lines...")
    transformed_lines = preprocess.get_transformed_lines(lines, transforms)

    logger.info("Creating a list of transformed log lines...")
    start_time = time.time()
    transformed_lines = [line for line in transformed_lines]
    logger.info("Elapsed time: %s" % (time.time() - start_time))
    logger.info("# transformed lines: %s" % len(transformed_lines))
    return transformed_lines

def test_logcluster(transformed_lines):
    SUPPORT = 50
    logcluster_file = "logcluster_input.txt"

    logger.info("Calling logcluster with support = %s" % SUPPORT)
    t = templates.logcluster(transformed_lines, file_path=logcluster_file, support=str(SUPPORT))
    return t

def test_stringmatch(transformed_lines):
    t = templates.stringmatch(transformed_lines)
    return t

if __name__ == "__main__":
    DIVIDER = "="*20
    transformed_lines_file = "transformed_lines.pickle"
    template_file = "templates.pickle"
    timed_template_file = "timed_templates.pickle"
    window_file = "windows.pickle"
    event_file = "events.pickle"

    logger.info("Step 1: preprocess")
    """
    transformed_lines = test_preprocess()
    logger.info("Writing transformed_lines to file: %s" % transformed_lines_file)
    with open(transformed_lines_file, 'wb') as pf:
        pickle.dump(transformed_lines, pf)
    """ 
    logger.info("Loading transformed_lines from file: %s" % transformed_lines_file)
    with open(transformed_lines_file, 'rb') as pf:
        transformed_lines = pickle.load(pf)    

    logger.info(DIVIDER)

    logger.info("Step 2: template")
    """
    t = test_logcluster(None)
    logger.info("Writing templates to file: %s", template_file)
    with open(template_file, 'wb') as pf:
        pickle.dump(t, pf)
    """
    logger.info("Loading templates from file: %s", template_file)
    with open(template_file, 'rb') as pf:
        t = pickle.load(pf)

    logger.info(DIVIDER)

    logger.info("Step 3: apply templates")
    """ 
    logger.info("Testing multiprocessing implementation (# cores: %s)", multiprocessing.cpu_count())
    start_time = time.time()
    timed_templates = apply.apply_templates(t, transformed_lines)
    logger.info("Elapsed time: %s", time.time()-start_time)
    logger.info("Writing timed templates to file: %s", timed_template_file)
    with open(timed_template_file, 'wb') as pf:
        pickle.dump(timed_templates, pf)
    """
    logger.info("Loading timed templates from file: %s", timed_template_file)
    with open(timed_template_file, 'rb') as pf:
        timed_templates = pickle.load(pf)

    logger.info(DIVIDER)

    logger.info("Step 4: create windows")
    """
    windows = windows.window(timed_templates)
    logger.info("Writing windows to file: %s" % window_file)
    with open(window_file, 'wb') as pf:
        pickle.dump(windows, pf)
    """

    logger.info("Loading windows from file: %s", window_file)
    with open(window_file, 'rb') as pf:
        windows = pickle.load(pf)

    logger.info(DIVIDER)

    logger.info("Step 5: discover events")
    events = events.fp_growth(windows, 10)
    logger.info("Writing events to file: %s", event_file)
    with open(event_file, 'wb') as pf:
        pickle.dump(events, pf)

    """
    logger.info("Loading events from file: %s", event_file)
    with open(event_file, 'rb') as pf:
        events = pickle.load(pf)
    """
    
    logger.info(DIVIDER)
