import os

from magichour.api.local.sample.steps.evalapply import evalapply_step
from magichour.api.local.sample.steps.evalwindow import evalwindow_step
from magichour.api.local.sample.steps.event import event_step
from magichour.api.local.sample.steps.genapply import genapply_step
from magichour.api.local.sample.steps.genwindow import genwindow_step
from magichour.api.local.sample.steps.preprocess import preprocess_step
from magichour.api.local.sample.steps.template import template_step

from magichour.api.local.util.log import get_logger, log_time
from magichour.api.local.util.pickl import read_pickle_file, write_pickle_file

logger = get_logger(__name__)
sample_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(sample_dir, "data")

# Result caching (to help w/ debugging)

pickle_cache_dir = os.path.join(data_dir, "pickle")
transformed_lines_file = os.path.join(pickle_cache_dir, "transformed_lines.pickle")
templates_file = os.path.join(pickle_cache_dir, "templates.pickle")
timed_templates_file = os.path.join(pickle_cache_dir, "timed_templates.pickle")
modelgen_windows_file = os.path.join(pickle_cache_dir, "modelgen_windows.pickle")
events_file = os.path.join(pickle_cache_dir, "events.pickle")
modeleval_windows_file = os.path.join(pickle_cache_dir, "modeleval_windows.pickle")
timed_events_file = os.path.join(pickle_cache_dir, "timed_events.pickle")

###

# Inputs

input_dir = os.path.join(data_dir, "input")
log_file = os.path.join(input_dir, "tbird.log.500k")
transforms_file = os.path.join(data_dir, "sample.transforms")

###

# Parameters for pipeline

read_lines_args = [0, 10]
read_lines_kwargs = {"skip_num_chars": 22}

logcluster_kwargs = {"support": "50"}

modelgen_windows_kwargs = {"window_size": 60, "tfidf_threshold": 0}

paris_kwargs = {"r_slack": None}
fp_growth_kwargs = {"min_support": 0.005, "iterations": 10000} #only return 10000 itemsets, iterations = -1 will return all

###

@log_time
def main():
    loglines = preprocess_step(log_file, transforms_file, *read_lines_args, **read_lines_kwargs)
    write_pickle_file(loglines, transformed_lines_file)
    #loglines = read_pickle_file(transformed_lines_file)
    
    gen_templates = template_step(loglines, "logcluster", **logcluster_kwargs)
    #gen_templates = template_step(loglines, "stringmatch") # WIP
    write_pickle_file(gen_templates, templates_file)
    #gen_templates = read_pickle_file(templates_file)
    
    timed_templates = genapply_step(loglines, gen_templates)
    write_pickle_file(timed_templates, timed_templates_file)
    #timed_templates = read_pickle_file(timed_templates_file)
    
    modelgen_windows = genwindow_step(timed_templates, **modelgen_windows_kwargs)
    write_pickle_file(modelgen_windows, modelgen_windows_file)
    #modelgen_windows = read_pickle_file(modelgen_windows_file)

    gen_events = event_step(modelgen_windows, "fp_growth", **fp_growth_kwargs)
    #gen_events = event_step(modelgen_windows, "paris", **paris_kwargs) # WIP
    write_pickle_file(gen_events, events_file)
    #gen_events = read_pickle_file(events_file)

    """
    # pretty print
    template_d = {template_id : template for (template_id, template) in [(template.id, template) for template in gen_templates]}
    e = []
    for event in gen_events:
        ts = []
        for template_id in event.template_ids:
            #ts.append(template_id)
            ts.append("%s: %s" % (template_id, template_d[template_id].str))
        e.append(ts)
    from pprint import pformat
    logger.info("Discovered events:")
    logger.info("\n"+pformat(e))
    """

    modeleval_windows = evalwindow_step(timed_templates, window_size)
    write_pickle_file(modeleval_windows, modeleval_windows_file)
    #modeleval_windows = read_pickle_file(modeleval_windows_file)

    timed_events = evalapply_step(gen_events, modeleval_windows)
    write_pickle_file(timed_events, timed_events_file)
    #timed_events = read_pickle_file(timed_events_file)

    logger.info("Done!")
    
if __name__ == "__main__":
    main()
