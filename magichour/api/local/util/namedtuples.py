from collections import namedtuple

LogLine = namedtuple("LogLine", ["id", "ts", "text", "processed", "replacements", "supportId"])


Transform = namedtuple('Transform', ['id', 'type', 'name', 'transform', 'compiled'])


Template = namedtuple("Template", ["id", "match", "str"])


TimedTemplate = namedtuple("TimedTemplate", ["ts", "template_id", "logline_id"])


ModelGenWindow = namedtuple("ModelGenWindow", ["template_ids"])
#ModelGenWindow = namedtuple("ModelGenWindow", ["id", "template_ids"])


ModelEvalWindow = namedtuple("ModelEvalWindow", ["start_time", "end_time", "timed_templates"])
#ModelEvalWindow = namedtuple("ModelEvalWindow", ["id", "timed_templates"])


Event = namedtuple("Event", ["id", "template_ids"])


TimedEvent = namedtuple("TimedEvent", ["event_id", "timed_templates"])