import glob
import operator
import os

from magichour.api.local.modelgen.preprocess import log_cardinality
from magichour.api.local.sample.steps.evalapply import evalapply_step
from magichour.api.local.sample.steps.event import event_step
from magichour.api.local.sample.steps.genapply import genapply_step
from magichour.api.local.sample.steps.genwindow import genwindow_step
from magichour.api.local.sample.steps.preprocess import preprocess_step
from magichour.api.local.sample.steps.template import template_step
from magichour.api.local.util.log import get_logger, log_time
from magichour.api.local.util.namedtuples import strTimedEvent
from magichour.api.local.util.pickl import write_pickle_file
from magichour.validate.datagen.eventgen import auditd

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
def run_pipeline(options):
    read_lines_kwargs = {'transforms_file': options.transforms_file,
                         'gettime_auditd': options.auditd, 
                         'type_template_auditd': options.auditd_templates_file,
                         'ts_start_index': options.ts_start_index, 
                         'ts_end_index': options.ts_end_index,
                         'ts_format': options.ts_format,
                         'skip_num_chars': options.skip_num_chars,
                         'mp': options.mp,}

    loglines = []

    log_files = []
    if options.data_file:
        log_files.append(options.data_file)
    if options.data_dir:
        log_files.extend(glob.glob(os.path.join(options.data_dir, '*')))
    if not log_files or (not options.data_file and not options.data_dir):
        raise RuntimeError('No input specified/available')

    for log_file in log_files:
        loglines.extend(
            preprocess_step(
                log_file,
                **read_lines_kwargs))

    # count cardinality; print unique lines if verbose and there are actually
    # transforms to apply
    log_cardinality(loglines, 
                    get_item=operator.attrgetter('processed'), 
                    item_title='Transform', 
                    verbose=options.verbose and options.transforms_file)

    if options.save_intermediate:
        transformed_lines_file = os.path.join(
            options.pickle_cache_dir, "transformed_lines.pickle")
        write_pickle_file(loglines, transformed_lines_file)

    if read_lines_kwargs.get('type_template_auditd'):
        # Read in auditd template definitions
        templates = get_auditd_templates(options.auditd_templates_file)
    else:
        # Generate templates
        if options.template_gen == 'logcluster':
            logcluster_kwargs = {"support": str(options.template_support)}
            templates = template_step(
                loglines, "logcluster", **logcluster_kwargs)
        elif options.template_gen == 'stringmatch':
            templates = template_step(loglines, "stringmatch")  # WIP
        else:
            raise NotImplementedError(
                '%s Template generation method not implemented' %
                options.template_gen)

        if options.save_intermediate:
            templates_file = os.path.join(
                options.pickle_cache_dir, "templates.pickle")
            write_pickle_file(templates, templates_file)

        log_cardinality(templates, 
                        item_key=operator.attrgetter('id'), 
                        item_title='Template', 
                        verbose=options.verbose)

    timed_templates = genapply_step(loglines, templates, **read_lines_kwargs)
    if options.save_intermediate:
        timed_templates_file = os.path.join(
            options.pickle_cache_dir, "timed_templates.pickle")
        write_pickle_file(timed_templates, timed_templates_file)

    modelgen_windows = genwindow_step(timed_templates, 
                                      window_size=options.gwindow_time, 
                                      tfidf_threshold=options.gtfidf_threshold)
    if options.save_intermediate:
        modelgen_windows_file = os.path.join(
            options.pickle_cache_dir, "modelgen_windows.pickle")
        write_pickle_file(modelgen_windows, modelgen_windows_file)

    if options.event_gen == 'fp-growth':
        fp_growth_kwargs = {
            "min_support": options.min_support,
            "iterations": options.iterations,
            "tfidf_threshold": options.tfidf_threshold}
        gen_events = event_step(
            modelgen_windows,
            "fp_growth",
            **fp_growth_kwargs)
    elif options.event_gen == 'paris':
        paris_kwargs = {
            "r_slack": options.r_slack,
            "num_iterations": options.num_iterations,
            "tau": options.tau}
        gen_events = event_step(
            modelgen_windows,
            "paris",
            **paris_kwargs)  # WIP
    elif options.event_gen == 'glove':
        glove_kwargs = {
            'num_components': options.num_components, 
            'glove_window': options.glove_window, 
            'epochs': options.epochs}
        gen_events = event_step(
            modelgen_windows, 
            "glove", 
            verbose=options.verbose, 
            **glove_kwargs)
    elif options.event_gen == 'auditd':
        # ignore timed_templates and modelgen_window and pass templates to auditd-specific event generator
        gen_events = auditd.event_gen(templates)
    else:
        raise NotImplementedError('%s Not implemented' % options.event_gen)

    if options.save_intermediate:
        events_file = os.path.join(options.pickle_cache_dir, "events.pickle")
        write_pickle_file(gen_events, events_file)

    logger.info("Discovered events: %d" % len(gen_events))
    if options.verbose:
        # Print events and their templates
        if read_lines_kwargs.get('type_template_auditd'):
            template_list = [(templates[template], template) 
                             for template in templates]
        else:
            template_list = [(template.id, template) for template in templates]

        template_d = {
            template_id: template for (
                template_id,
                template) in template_list}
        e = []
        for event in sorted(gen_events, key=lambda event:event.id):
            ts = ["event_id: %s" % event.id]
            for template_id in sorted(event.template_ids):
                ts.append("%s: %s" % (template_id, template_d[template_id]))
            e.append(ts)
        from pprint import pformat
        logger.info("\n" + pformat(e))

        # compute how many times each template was used (i.e. how many events each template appears in)
        event_templates = (
            template_d[template_id] for event in gen_events for template_id in event.template_ids)
        log_cardinality(
            event_templates, 
            item_title='EventTemplate', 
            item_key=operator.attrgetter('id'), 
            verbose=options.verbose)

    timed_events = evalapply_step(
        gen_events, timed_templates, window_time=options.awindow_time, mp=options.mp)
    if options.save_intermediate:
        timed_events_file = os.path.join(
            options.pickle_cache_dir, "timed_events.pickle")
        write_pickle_file(timed_events, timed_events_file)

    logger.info("Timed events: %d" % len(timed_events))
    log_cardinality(
        timed_events, 
        item_title='TimedEvent', 
        get_item=operator.attrgetter('event_id'), 
        verbose=options.verbose)
    if options.verbose > 1:
        # Print timed event summary for -vv
        
        # sort timed_templates in ascending time order
        for te in timed_events:
            te.timed_templates.sort(key=lambda tt: tt.ts)

        if options.sort_events_key=='time':
            # sort timed events in ascending time order (of their first occurring timed_template)
            timed_event_key = lambda te: te.timed_templates[0].ts
        else:
            # sort timed events by event id, then by time order
            timed_event_key = lambda te: (te.event_id, te.timed_templates[0].ts)
        timed_events.sort(key=timed_event_key)

        e = []
        for event in timed_events:
            s = strTimedEvent(event)
            e.append(s)
        logger.info("\n" + pformat(e))

    logger.info("Done!")


def main():
    from argparse import ArgumentParser
    import sys

    logger.info('args: %s', ' '.join(sys.argv[1:]))
    # NOTE: parser.add_argument() default value: default=None
    parser = ArgumentParser()
    parser.add_argument(
        '-f',
        '--data-file',
        dest="data_file",
        help="Input log file")
    parser.add_argument(
        '-d',
        '--data-dir',
        dest="data_dir",
        help="Input log directory")
    parser.add_argument(
        '-t',
        '--transforms-file',
        dest="transforms_file",
        help="Transforms mapping file")
    parser.add_argument(
        '--template-gen',
        choices=[
            'logcluster',
            'stringmatch'],
        required=True)
    parser.add_argument(
        '--event-gen',
        choices=[
            'fp-growth',
            'paris',
            'glove',
            'auditd'],
        required=True)

    source_args = parser.add_argument_group('Source-specific Parameters')
    source_args.add_argument(
        '--auditd',
        default=False,
        help='Input is auditd logs',
        action="store_true")  # for now, this just means read auditd-timestamps
    source_args.add_argument(
        '--auditd_templates_file',
        dest="auditd_templates_file",
        help="CSV Mapping Auditd types to ids (if not specified Templates will be auto-generated)")
    source_args.add_argument(
        '--skip_num_chars', 
        default=0, 
        help='skip characters at beginning of each line')
    source_args.add_argument(
        '--ts_start_index', 
        default=0, 
        help='start of timestamp (after skipping)')
    source_args.add_argument(
        '--ts_end_index', 
        default=12, 
        help='end of timestamp (after skipping)')
    source_args.add_argument(
        '--ts_format', 
        help='datetime.strptime() format string')

    control_args = parser.add_argument_group('General Control Parameters')
    control_args.add_argument(
        '-w', 
        '--gwindow_time', 
        default=60, 
        help='Event model generate window size (seconds)')
    control_args.add_argument(
        '--gtfidf_threshold',
        default=None, # default = don't apply tfidf to model generation
        help='Event model generation tf_idf threshold')
    control_args.add_argument(
        '--awindow_time', 
        default=60, 
        help='Event application window size (seconds)')
    control_args.add_argument(
        '--template-support', 
        default=50, 
        help='# occurrences required to generate a Template')
    control_args.add_argument(
        '--mp', 
        default=False, 
        help='Turn on multi-processing', 
        action='store_true')

    fp_growth_args = parser.add_argument_group('FP-Growth Control Parameters')
    fp_growth_args.add_argument('--min_support', default=0.03, help='?')
    fp_growth_args.add_argument(
        '--iterations',
        default=-1,
        help='Number of itemsets to produce (-1 == all)')
    fp_growth_args.add_argument('--tfidf_threshold', default=0, help='?')

    paris_args = parser.add_argument_group('PARIS Control Parameters')
    paris_args.add_argument(
        '--r_slack',
        default=0,
        help='cost function parameter')
    paris_args.add_argument('--num_iterations', default=3, help='?')
    paris_args.add_argument(
        '--tau',
        default=1.0,
        help='cost function parameter')

    glove_args = parser.add_argument_group('Glove Control Parameters')
    glove_args.add_argument(
        '--num_components', 
        default=16, 
        help='?')
    glove_args.add_argument(
        '--glove_window', 
        default=10, 
        help='?')
    glove_args.add_argument(
        '--epochs', 
        default=20, 
        help='?')
    
    optional_args = parser.add_argument_group('Debug Arguments')
    optional_args.add_argument(
        '-v',
        '--verbose',
        dest='verbose',
        default=False,
        action="count",
        help="Print definitions")
    optional_args.add_argument(
        '--sort-events-key',
        choices=[
            'time',
            'event'],
        default='time',
        help="Sort events by time or event-id.")    
    optional_args.add_argument(
        "--save-intermediate",
        dest="save_intermediate",
        default=False,
        action="store_true",
        help="Save intermediate files which may result in large files")
    optional_args.add_argument(
        '--pickle_dir',
        dest="pickle_cache_dir",
        help="Directory for intermediate files")

    options = parser.parse_args()
    run_pipeline(options)

if __name__ == "__main__":
    main()
