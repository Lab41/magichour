from collections import namedtuple

LogLine = namedtuple("LogLine", ["t", "msg"])
Template = namedtuple("Template", ["id", "match", "str"])
TimedTemplate = namedtuple("TimedTemplate", ["t", "template_id"])
