from collections import namedtuple

LogLine = namedtuple('LogLine', ['id', 'ts', 'text', 'processed', 'replacements', 'supportId'])



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
DistributedLogLine = namedtuple('DLL',
                             ['ts', 'text',
                              'processed', 'pDict',
                              'template', 'templateId', 'tDict'])

'''
DistributedTransformLine - used for storing how to perform preProcessing

id - int: id of the transform
type - str: enum of how to handle the transform
name - str: name to use when replacing information
transform - str: how to perform the replacement given the type
compiled - compiled regex: compiled regex if applicable to the transform
'''

DistributedTransformLine = namedtuple('DTrL',
                                  ['id', 'type', 'name',
                                   'transform', 'compiled'])

'''
DistributedTemplateLine - helps determind which templates match a logline

id - int: id of the template
template - compiled regex: compiled regex to match a template
skipWords - list: list of skipwords found in the regex
'''

DistributedTemplateLine = namedtuple('DTeL', ['id', 'template', 'skipWords'])

Transform = namedtuple('Transform', ['id', 'type', 'name', 'transform', 'compiled'])


Template = namedtuple('Template', ['id', 'match', 'str'])


TimedTemplate = namedtuple('TimedTemplate', ['ts', 'template_id', 'logline_id'])


ModelGenWindow = namedtuple('ModelGenWindow', ['template_ids'])
#ModelGenWindow = namedtuple('ModelGenWindow', ['id', 'template_ids'])


ModelEvalWindow = namedtuple('ModelEvalWindow', ['start_time', 'end_time', 'timed_templates'])
#ModelEvalWindow = namedtuple('ModelEvalWindow', ['id', 'timed_templates'])


Event = namedtuple('Event', ['id', 'template_ids'])


TimedEvent = namedtuple('TimedEvent', ['event_id', 'timed_templates'])