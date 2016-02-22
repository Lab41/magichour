from collections import defaultdict
from magichour.api.local.util.namedtuples import Event, TimedEvent
from magichour.api.local.util.log import log_time
from magichour.api.local.modeleval.apply import apply_queue


def event_window(line, windowLength):
    '''
    alias events to the same key based off time

    Args:
        line(DistributedLogLine):
        windowLength(int): Length in seconds of the window to apply

    Retval:
        retval(tuple(window,DistributedLogLine))
    '''
    key = (line.templateId, int(line.ts / windowLength))
    value = line
    return (key, value)


def ship_events(line, t2e):
    '''
    Change keys from template based to event based
    When a template comes in, emit one value
    for each event that the template is in. making the new
    key (eventID,WindowID)
    value(DistributedLogLine)

    Args:
        line(DistributedLogLine)
        t23(Broadcast(defaultDict(set))): maps a template to the
                                     sensitized events

    Returns:
        retval(list(tuple(tuple(eventID,windowID), DistributedLogLine)))

    '''
    outList = list()
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

    windowed = rdd_log_lines.map(
        lambda line: event_window(
            line, window_length_distributed))
    edist = windowed.flatMap(
        lambda line: ship_events(
            line, template2event_broadcast))
    event_log_list = edist.groupByKey()
    timed_templates = event_log_list.flatMap(
        lambda input_tuple: apply_single_distributed_tuple(
            input_tuple, event2template_broadcast, window_time=window_length))

    return timed_templates
