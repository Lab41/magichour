from collections import namedtuple

TimedTemplate = namedtuple("TimedTemplate", ["t", "template_id"])
# probably better to rewrite this using map so that it can be parallelized
# -1 = did not match any templates

#lines = iterable of LogLines
#templates = output of functions in templates.py
def apply_templates(templates, loglines):
    """
    Applies the templates on an iterable. This function creates a list of TimedTemplate named tuples.
    The templates accepted by this function is exactly the output of functions in templates.py

    Args:
        templates:
        loglines:

    Returns:
        timed_templates:

    """
    timed_templates = list()
    for logline in loglines:
        timed_template = None #matched = False
        for template in templates:
            if template.match.match(logline.msg):
                timed_template = TimedTemplate(logline.t, template.id)
                break
        if not timed_template:
            timed_template = TimedTemplate(logline.t, -1)
        timed_templates.append(timed_template)
    return timed_templates
