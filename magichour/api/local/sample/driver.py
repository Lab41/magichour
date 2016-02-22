import os

from magichour.api.local.sample.steps.evalapply import evalapply_step
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
loglines_file = os.path.join(pickle_cache_dir, "loglines.pickle")
gen_templates_file = os.path.join(pickle_cache_dir, "gen_templates.pickle")
eval_loglines_file = os.path.join(pickle_cache_dir, "eval_loglines.pickle")
gen_windows_file = os.path.join(pickle_cache_dir, "gen_windows.pickle")
gen_events_file = os.path.join(pickle_cache_dir, "gen_events.pickle")
timed_events_file = os.path.join(pickle_cache_dir, "timed_events.pickle")

###

# Inputs

input_dir = os.path.join(data_dir, "input")
log_file = os.path.join(input_dir, "tbird.log.500k")
transforms_file = os.path.join(data_dir, "sample.transforms")

###

# Parameters for pipeline
write_to_pickle_file = False
read_lines_args = [{}, 0, 10]
read_lines_kwargs = {"skip_num_chars": 22}

logcluster_kwargs = {"support": "50"}

genapply_kwargs = {'mp': True}
gen_windows_kwargs = {"window_size": 60, "tfidf_threshold": 0}

glove_kwargs = {'num_components': 16, 'glove_window': 10, 'epochs': 20}
paris_kwargs = {"r_slack": 0.0, "num_iterations": 3}
# only return 10000 itemsets, iterations = -1 will return all
fp_growth_kwargs = {
    "min_support": 0.005,
    "iterations": 10000,
    "tfidf_threshold": 1.0}

eval_apply_kwargs = {'window_time': 60, 'mp': True}
###


@log_time
def main():
    loglines = preprocess_step(
        log_file,
        transforms_file,
        *read_lines_args,
        **read_lines_kwargs)
    if write_to_pickle_file:
        write_pickle_file(loglines, loglines_file)
    #loglines = read_pickle_file(loglines_file)

    gen_templates = template_step(loglines, "logcluster", **logcluster_kwargs)
    # gen_templates = template_step(loglines, "stringmatch") # WIP
    if write_to_pickle_file:
        write_pickle_file(gen_templates, gen_templates_file)
    #gen_templates = read_pickle_file(gen_templates_file)

    eval_loglines = genapply_step(loglines, gen_templates, **genapply_kwargs)
    if write_to_pickle_file:
        write_pickle_file(eval_loglines, eval_loglines_file)
    #eval_loglines = read_pickle_file(eval_loglines_file)

    gen_windows = genwindow_step(eval_loglines, **gen_windows_kwargs)
    if write_to_pickle_file:
        write_pickle_file(gen_windows, gen_windows_file)
    #gen_windows = read_pickle_file(modelgen_windows_file)

    #gen_events = event_step(gen_windows, "fp-growth", **fp_growth_kwargs)
    #gen_events = event_step(gen_windows, "paris", **paris_kwargs)
    gen_events = event_step(gen_windows, "glove", **glove_kwargs)
    if write_to_pickle_file:
        write_pickle_file(gen_events, gen_events_file)
    #gen_events = read_pickle_file(gen_events_file)

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

    timed_events = evalapply_step(
        gen_events,
        eval_loglines,
        **eval_apply_kwargs)
    write_pickle_file(timed_events, timed_events_file)
    #timed_events = read_pickle_file(timed_events_file)

    logger.info("Done!")

if __name__ == "__main__":
    main()
