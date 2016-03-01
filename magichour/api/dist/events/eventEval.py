from collections import defaultdict
from magichour.api.local.util.namedtuples import Event
from magichour.api.local.util.log import log_time
from magichour.api.local.modeleval.apply import apply_queue
import math


def event_window(line, window_length, window_overlap=None):
    '''
    alias events to the same key based off time

    Args:
        line(DistributedLogLine): a log line that has been through template processing
        window_length(int): length of the window in seconds
        window_overlap (float): fraction of window where log msgs should go in both windows

    Retval:
        retval(tuple(window,DistributedLogLine))
    '''
    output = []
    window = float(line.ts) / window_length

    key = (line.templateId, (int(window)))
    output.append((key, line))
    if window_overlap:
        delta = window - math.floor(window)
        # Since we are truncating near the window boundary can can be close
        # to zero or close to 1
        if delta <= window_overlap or delta >= 1 - window_overlap:
            if delta > 0:
                # Also output to previous window
                key = (line.templateId, (int(window) - 1))
                output.append((key, line))
            elif delta < 0:
                # Also output to next window
                key = (line.templateId, (int(window) + 1))
                output.append((key, line))
    return output


def ship_events(line, t2e):
    '''
    Change keys from template based to event based
    When a template comes in, emit one value
    for each event that the template is in. making the new
    key (eventID,WindowID)
    value(DistributedLogLine)

    Args:
        line(DistributedLogLine)
        t2e(Broadcast(defaultDict(set))): maps a template to the
                                     sensitized events

    Returns:
        retval(list(tuple(tuple(eventID,windowID), DistributedLogLine)))

    '''
    outList = list()
    print line
    key, value = line
    templateId, timeBucket = key
    for event in t2e.value[int(templateId)]:
        outList.append(((int(event),
                         timeBucket),
                        value))
    return outList


def make_lookup_dicts(event_defs):
    '''
    make the lookup dictionaries used for translating
    between templates and events which care about specific
    templates

    Args:
        event_defs(list(Event)): list of templates which go together

    Returns:
        retval(tuple(defaultdict(set),defaultdict(set))):
            (templates->events, events->templates)
    '''
    template2event = defaultdict(set)
    event2template = defaultdict(set)
    for eventDef in event_defs:
        items = eventDef.template_ids
        for item in items:
            event2template[eventDef.id].add(int(item))

    for k, v in event2template.iteritems():
        for item in v:
            template2event[item].add(int(k))

    return(template2event, event2template)


def apply_single_distributed_tuple(
        input_tuple,
        event2template_broadcast,
        window_time=None):
    """
    Helper function that takes a tuple as input and breaks out inputs to pass
    to apply_queue
    Args:
        input_tuple(tuple(tuple(event_id, window_num), iterable(DistributedLogLines))):
                    A tuple of inputs to be split and passed
        event2template_broadcast (broadcast variable): Dictionary mapping event_ids to templates contained

    Returns:
        timed_events (list(TimedEvent)): A list of found events with their component log lines
    """
    event_description, log_msgs = input_tuple
    event_id, window_num = event_description

    event = Event(id=event_id, template_ids=list(
        event2template_broadcast.value[event_id]))
    # Comes in as iterable, follow on functions expect list
    log_msgs = list(log_msgs)

    return apply_queue(event, log_msgs, window_time=window_time)


@log_time
def event_eval_rdd(sc, rdd_log_lines, event_list,
                   window_length=120, window_length_distributed=6000):
    '''
    Performs the event generation from incoming DistributedLogLine rdd

    Args:
        sc(sparkContext):
        rdd_log_lines(DistributedLogLines): rdd of DistributedLogLines created
        by earlier processing
        event_list(list(Event)): List of event definitions
        window_length(int): window length to evaluate localy events in (seconds)
        window_length_distributed(int): In parallelizing event evaluation this parameter controls how large of
                    a window should go to each reducer. Events spanning this boundry will not be found. This
                    should be much larger than window_length or performance will suffer

    Returns:
        retval(rdd tuple(tuple(eventId,windowID),tuple(DistributedLogLines)))

    '''

    template2event, event2template = make_lookup_dicts(event_list)
    template2event_broadcast = sc.broadcast(template2event)
    event2template_broadcast = sc.broadcast(event2template)

    # fraction of window to push to adjacent windows
    window_overlap = float(window_length) / window_length_distributed

    windowed = rdd_log_lines.map(
        lambda line: event_window(
            line, window_length_distributed, window_overlap=window_overlap))
    edist = windowed.flatMap(
        lambda line: ship_events(
            line, template2event_broadcast))
    event_log_list = edist.groupByKey()
    timed_templates = event_log_list.flatMap(
        lambda input_tuple: apply_single_distributed_tuple(
            input_tuple, event2template_broadcast, window_time=window_length))

    return timed_templates
