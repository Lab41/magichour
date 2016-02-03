import functools
import multiprocessing

from magichour.api.local.named_tuples import TimedTemplate
from magichour.api.local.logging_util import get_logger

logger = get_logger(__name__)

def process_line(templates, logline):
    for template in templates:
        if template.match.match(logline.text):
            return TimedTemplate(logline.ts, template.id)
    # -1 = did not match any template
    return TimedTemplate(logline.ts, -1)

def apply_templates(templates, loglines, mp=True):
    """
    Applies the templates on an iterable. This function creates a list of TimedTemplate named tuples.
    In effect this will produce a list of which templates occurred at which times.
    -1 is the template_id that is used for a logline which was unable to be matched to a template.

    The templates accepted by this function is exactly the output of functions in templates.py
    This function has the option of running in either multiprocessing mode (mp=True by default) or not.

    Args:
        templates: iterable Templates to apply
        loglines: loglines which will be examined

    Kwargs:
        mp: whether or not to run in multiprocessing mode (default: True)

    Returns:
        timed_templates: a list of TimedTemplate named tuples that represent which templates occurred at which times in the log file.

    """
    if mp:
        # Use multiprocessing.Pool to use multiple CPUs
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        f = functools.partial(process_line, templates)

        timed_templates = pool.map(func=f, iterable=loglines)
    else:
        # Do this the naive way with one CPU
        timed_templates = []
        for logline in loglines:
            timed_templates.append(process_line(templates, logline))
    return timed_templates
