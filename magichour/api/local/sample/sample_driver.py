from magichour.api.local.logging_util import get_logger

from magichour.api.local.preprocess import preprocess
from magichour.api.local.templates import templates, apply
from magichour.api.local.windows import windows
from magichour.api.local.events import events

import cPickle as pickle
import time

logger = get_logger(__name__)

# Stick this as a decorator on any function to print the # of time spent in that function.
def log_time(f):
    def wrapper(*args, **kwargs):
        tstart = time.time()
        result = f(*args, **kwargs)
        m, s = divmod(time.time()-tstart, 60)
        msg = "Time in %s(): "
        if m == 0:
            logger.info(msg+"%s seconds", f.__name__, s)
        else:
            logger.info(msg+"%s minutes, %s seconds", f.__name__, m, s)
        return result
    return wrapper

###

@log_time
def read_transforms_substep(transforms_file):
    # These transforms are tailored to this dataset.
    # You will likely need to write your own transforms for your own data.
    logger.info("Reading transforms from file: %s" % transforms_file)
    transforms = preprocess.get_transforms(transforms_file)
    return transforms

@log_time
def read_lines_substep(log_file, *args, **kwargs):
    logger.info("Reading log lines from file: %s" % log_file)
    lines = preprocess.get_lines(log_file, *args, **kwargs)
    return lines

@log_time
def transformed_lines_substep(lines, transforms):
    logger.info("Transforming log lines...")
    transformed_lines = preprocess.get_transformed_lines(lines, transforms)
    return transformed_lines

@log_time
def _transformed_lines_to_list_substep(transformed_lines):
    return [line for line in transformed_lines]

# Step 1
@log_time
def preprocess_step(log_file, transforms_file, *args, **kwargs):
    transforms = read_transforms_substep(transforms_file)
    lines = read_lines_substep(log_file, *args, **kwargs)
    transformed_lines = transformed_lines_substep(lines, transforms)
    
    # get_transformed_lines returns a generator. This converts it to a list.
    transformed_lines = _transformed_lines_to_list_substep(transformed_lines)
    return transformed_lines

###

@log_time
# file_path=logcluster_file, support=str(LOGCLUSTER_SUPPORT)
def logcluster_substep(lines, *args, **kwargs):
    logger.info("Running logcluster... (%s)", kwargs)
    gen_templates = templates.logcluster(lines, *args, **kwargs)
    return gen_templates
                                                                                       
@log_time
def stringmatch_substep(lines, *args, **kwargs):
    logger.info("Running stringmatch...")
    gen_templates = templates.stringmatch(lines, *args, **kwargs)
    return gen_templates
    
# Step 2
@log_time
def template_step(lines, template_algorithm="logcluster", *args, **kwargs):
    CHOICES = {"logcluster": logcluster_substep, "stringmatch": stringmatch_substep}
    template_fn = CHOICES.get(template_algorithm, None)
    if not template_fn:
        error_msg = "template_algorithm must be one of: %s" % CHOICES
        logger.error(error_msg)
        raise Exception(error_msg)
    logger.info("Running template_algorithm %s on log lines...", template_algorithm)
    gen_templates = template_fn(lines, *args, **kwargs)
    return gen_templates

###

# Step 3  
@log_time
def apply_templates_step(lines, gen_templates):
    logger.info("Applying templates to lines...")
    timed_templates = apply.apply_templates(gen_templates, lines)
    return timed_templates

###

# Step 4
@log_time
def window_step(timed_templates, *args, **kwargs):
    logger.info("Creating windows from timed_templates...")
    gen_windows = windows.window(timed_templates, *args, **kwargs)
    return gen_windows

###

@log_time
def paris_substep(gen_windows, *args, **kwargs):
    logger.info("Running PARIS algorithm... (%s)", kwargs)
    gen_events = events.paris(gen_windows, *args, **kwargs)
    return gen_events

@log_time
def fp_growth_substep(gen_windows, *args, **kwargs):
    logger.info("Running fp_growth algorithm... (%s)", kwargs)
    gen_events = events.fp_growth(gen_windows, *args, **kwargs)
    return gen_events
    
# Step 5
@log_time
def event_step(gen_windows, event_algorithm="fp_growth", *args, **kwargs):
    CHOICES = {"fp_growth": fp_growth_substep, "paris": paris_substep}
    event_fn = CHOICES.get(event_algorithm, None)
    if not event_fn:
        raise Exception("event_algorithm must be one of: %s" % CHOICES)
    logger.info("Running event algorithm %s on windows...")
    gen_events = event_fn(gen_windows, *args, **kwargs)
    return gen_events
                
###

# Step 6
@log_time
def apply_events_step():
    pass

###

# Result caching (to help w/ debugging)

transformed_lines_file = "transformed_lines.pickle"
template_file = "templates.pickle"
timed_template_file = "timed_templates.pickle"
window_file = "windows.pickle"
event_file = "events.pickle"

@log_time
def read_pickle_file(pickle_file):
    logger.info("Reading pickle file: %s", pickle_file)
    with open(pickle_file, 'rb') as pf:
        data = pickle.load(pf)
    return data

@log_time
def write_pickle_file(data, pickle_file):
    logger.info("Writing data to pickle file: %s", pickle_file)
    with open(pickle_file, 'wb') as pf:
        pickle.dump(data, pf)

###

log_file = "tbird.log.500k"
transforms_file = "simpleTrans"
read_lines_args = [0, 10]
read_lines_kwargs = {"skip_num_chars": 22}
window_size = 5
logcluster_kwargs = {"support": "50"}
paris_kwargs = {"r_slack": None}
fp_growth_kwargs = {"min_support": 10}

@log_time
def main():
    loglines = preprocess_step(log_file, transforms_file, *read_lines_args, **read_lines_kwargs)
    write_pickle_file(loglines, transformed_lines_file)
    #loglines = read_pickle_file(transformed_lines_file)
    
    gen_templates = template_step(loglines, "logcluster", **logcluster_kwargs)
    #gen_templates = template_step(loglines, "stringmatch")
    write_pickle_file(gen_templates, template_file)
    #gen_templates = read_pickle_file(template_file)
    
    timed_templates = apply_templates_step(loglines, gen_templates)
    write_pickle_file(timed_templates, timed_template_file)
    #timed_templates = read_pickle_file(timed_template_file)
    
    windows = window_step(timed_templates, window_size)
    write_pickle_file(windows, window_file)
    #windows = read_pickle_file(window_file)
    
    ### THIS PART IS STILL WIP
    #gen_events = event_step(windows, "fp_growth", **fp_growth_kwargs)
    #gen_events = event_step(windows, "paris", **paris_kwargs)
    #write_event_file(gen_events, events_file)
    #gen_events = read_pickle_file(event_file)
    
    logger.info("Done!")
    
if __name__ == "__main__":
    main()