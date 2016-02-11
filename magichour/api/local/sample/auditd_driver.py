import os
import glob

from magichour.api.local.modelgen.preprocess import cardinality_transformed_lines

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


def get_auditd_templates(auditd_templates_file):
    """
    Helper function to read in auditd type to id mapping and return lookup dictionary
    """
    auditd_templates = {}
    for line in open(auditd_templates_file):
        type_field, id = line.rstrip().split(',')
        auditd_templates[type_field] = int(id)
    return auditd_templates


@log_time
def run_auditd_pipeline(options):
    auditd_kwargs = {'gettime_auditd': True, 
                     'type_template_auditd': not options.transforms_file}  # use type_templates if no transforms file
    
    loglines = []
    for log_file in glob.glob(os.path.join(options.data_dir, '*')):
        loglines.extend(preprocess_step(log_file, transforms_file=options.transforms_file, **auditd_kwargs))

    # count cardinality; print unique lines if verbose and there are actually transforms to apply
    (countLines, countUniqueLines, percentUniqueLines, uniqLines) = cardinality_transformed_lines(loglines, options.verbose and options.transforms_file)

    if options.save_intermediate:
        transformed_lines_file = os.path.join(options.pickle_cache_dir, "transformed_lines.pickle")
        write_pickle_file(loglines, transformed_lines_file)

    if auditd_kwargs.get('type_template_auditd'):
        # Read in auditd template definitions
        templates = get_auditd_templates(options.auditd_templates_file)
    else:
        # Generate templates
        if options.template_gen =='logcluster':
            logcluster_kwargs = {"support": "50"}
            templates = template_step(loglines, "logcluster", **logcluster_kwargs)
        elif options.template_gen =='stringmatch':
            templates = template_step(loglines, "stringmatch") # WIP
        else:
            raise NotImplementedError('%s Template generation method not implemented'%options.template_gen)

        if options.save_intermediate:
            templates_file = os.path.join(options.pickle_cache_dir, "templates.pickle")
            write_pickle_file(templates, templates_file)

    timed_templates = genapply_step(loglines, templates, **auditd_kwargs)
    if options.save_intermediate:
        timed_templates_file = os.path.join(options.pickle_cache_dir, "timed_templates.pickle")
        write_pickle_file(timed_templates, timed_templates_file)

    modelgen_windows = genwindow_step(timed_templates, options.window_size)
    if options.save_intermediate:
        modelgen_windows_file = os.path.join(options.pickle_cache_dir, "modelgen_windows.pickle")
        write_pickle_file(modelgen_windows, modelgen_windows_file)


    if options.event_gen =='fp-growth':
        fp_growth_kwargs = {"min_support": 0.03, "iterations": -1} #only return 10000 itemsets, iterations = -1 will return all
        gen_events = event_step(modelgen_windows, "fp_growth", **fp_growth_kwargs)
    elif options.event_gen == 'paris':
        paris_kwargs = {"r_slack": 0, "num_iterations":3}
        gen_events = event_step(modelgen_windows, "paris", **paris_kwargs) # WIP
    else:
        raise NotImplementedError('%s Not implemented'%options.event_gen)

    if options.save_intermediate:
        events_file = os.path.join(options.pickle_cache_dir, "events.pickle")
        write_pickle_file(gen_events, events_file)

    if options.verbose:
        # Print templates
        if auditd_kwargs.get('type_template_auditd'):
            template_list = [(templates[template], template) for template in templates]
        else:
            template_list = [(template.id, template) for template in templates]
            
        template_d = {template_id : template for (template_id, template) in template_list}
        e = []
        for event in gen_events:
            ts = []
            for template_id in event.template_ids:
                ts.append("%s: %s" % (template_id, template_d[template_id]))
            e.append(ts)
        from pprint import pformat
        logger.info("Discovered events:")
        logger.info("\n"+pformat(e))

    """
    modeleval_windows = evalwindow_step(timed_templates, options.window_size)
    if options.save_intermediate:
        modeleval_windows_file = os.path.join(options.pickle_cache_dir, "modeleval_windows.pickle")
        write_pickle_file(modeleval_windows, modeleval_windows_file)
    """

    timed_events = evalapply_step(gen_events, timed_templates, loglines)
    if options.save_intermediate:
        timed_events_file = os.path.join(options.pickle_cache_dir, "timed_events.pickle")
        write_pickle_file(timed_events, timed_events_file)

    logger.info("Done!")

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-d', '--data-dir', dest="data_dir", help="Input log directory")
    parser.add_argument('-t', '--transforms-file', dest="transforms_file", help="Transforms mapping file", default=None)
    parser.add_argument('--auditd_templates_file', dest="auditd_templates_file", help="CSV Mapping Auditd types to ids", default=None)
    parser.add_argument('--template-gen', choices=['logcluster', 'stringmatch'])
    parser.add_argument('--event-gen', choices=['fp-growth', 'paris'])

    control_args =  parser.add_argument_group('Control Parameters')
    control_args.add_argument('-w', '--window_size', default=60, help='Window size to use (seconds)')

    optional_args =  parser.add_argument_group('Debug Arguments')
    optional_args.add_argument('-v', '--verbose', dest='verbose', default=False, action="store_true",
                      help="Print definitions")
    optional_args.add_argument("--save-intermediate", dest="save_intermediate", default=False, action="store_true",
                      help="Save intermediate files which may result in large files")
    optional_args.add_argument('--pickle_dir', dest="pickle_cache_dir", help="Directory for intermediate files")

    options = parser.parse_args()
    run_auditd_pipeline(options)

if __name__ == "__main__":
    main()
