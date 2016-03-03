from collections import namedtuple


'''
DistributedLine - moves information between various stages of algorithms

ts - float(timestamp)
text -original message
processed - output of PreProcessing
pDict - dictionary of PreProcessing replacements
template - template generated
templateId - int of the template id
tDict - dictionary of any template related replacements

NOTE: text, and template are baggage for now


'''
DistributedLogLine = namedtuple('DistributedLogLine',
                                ['ts', 'text',
                                 'processed', 'proc_dict',
                                 'template', 'templateId', 'template_dict'])

'''
DistributedTransformLine - used for storing how to perform preProcessing

id - int: id of the transform
type - str: enum of how to handle the transform
name - str: name to use when replacing information
transform - str: how to perform the replacement given the type
compiled - compiled regex: compiled regex if applicable to the transform
'''

DistributedTransformLine = namedtuple('DistributedTransformLine',
                                      ['id', 'type', 'name',
                                       'transform', 'compiled'])

'''
DistributedTemplateLine - helps determine which templates match a logline

id - int: id of the template
template - compiled regex: compiled regex to match a template
skip_words - list: list of skipwords found in the regex
raw_str - str: The raw string used to generate the tempalte/skip_words
'''

DistributedTemplateLine = namedtuple(
    'DistributedTemplateLine', [
        'id', 'template', 'skip_words', 'raw_str'])


Event = namedtuple('Event', ['id', 'template_ids'])


TimedEvent = namedtuple('TimedEvent', ['event_id', 'timed_templates'])


def strTimedEvent(timed_event):
    from datetime import datetime
    from operator import attrgetter

    tt = sorted(timed_event.timed_templates, key=attrgetter('ts'))
    L = len(tt)
    if L == 0:
        return ""
    t_start = tt[0].ts
    t_end = tt[-1].ts
    t_median = tt[
        L / 2].ts if L % 2 > 0 else (tt[L / 2 - 1].ts + tt[L / 2].ts) / 2.0
    duration = t_end - t_start
    median_offset = t_median - t_start
    dt_start = datetime.utcfromtimestamp(t_start)
    dt_end = datetime.utcfromtimestamp(t_end)
    dt_median = datetime.utcfromtimestamp(t_median)
    dt_duration = dt_end - dt_start
    dt_median_offset = dt_median - dt_start

    return "TimedEvent: event_id=%-36s, start=%14.3f, end=%14.3f, median=%14.3f, duration=%10.3f, median_offset=%10.3f; s=%s, e=%s, m=%s, d=%s, mo=%s" % (
        timed_event.event_id, t_start, t_end, t_median, duration, median_offset, dt_start, dt_end, dt_median, dt_duration, dt_median_offset)
