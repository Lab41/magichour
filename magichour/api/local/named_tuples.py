from collections import namedtuple

LogLine = namedtuple("LogLine", ["ts", "text", "processed", "replacements", "supportId"])


Transform = namedtuple('Transform', ['id', 'type', 'name', 'transform', 'compiled'])


Template = namedtuple("Template", ["id", "match", "str"])


TimedTemplate = namedtuple("TimedTemplate", ["ts", "template_id"])
