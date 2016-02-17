from collections import defaultdict
from magichour.api.local.util.namedtuples import TimedEvent


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


def make_events_from_lines(line, e2t):
    '''
    Evaluate if an event has been seen in a window of templates

    many ways of immediately doing this.
  no    0. keep a FSM for each event and output  when they fsm reaches
           the accptance state [not doing this]
  no    1. just keep set of seen templates within the window and see
           if an event is a subset of the window. [not doing this
           as events may belong to different sources, although it is fast,
           perhaps would be a good test to see if further processing needed.]
 yes->  2. keep a running set evaluation for templates in a set
 yes->          1. choose to only keep the most recent version of a toemplate
                [has the effect of lessening the timespread of the
                 templates chosen.]
                OR
  no  x         2. choose to keep the first version of  a templateo
                [not doint this
                has the effect of spreading out the templates chosen]

    Args:
        line(DistributedLogLine):
        e2t(Broadcast(defaultDict(set))): mapping between events and templates

    Returns:
        retval(list(tuple(tuple(eventID,windowID),tuple(DistributedLogLines))))
    '''

    key, iterable = line
    event, timeBin = key

    # what set are we looking to satisfy
    lookingFor = e2t.value[event]

    tList = list()
    for i in iterable:
        tList.append(i)

    # make sure list is in timeseries order
    # TODO does this really need to occur?
    tList.sort()

    # where the output goes
    outSet = set()

    tempDict = dict()
    tempSet = set()

    for outer in range(len(tList)):
        tempDict.clear()
        tempSet.clear()
        for inner in range(outer, len(tList)):
            tempDict[tList[inner].templateId] = tList[inner]
            tempSet.add(tList[inner].templateId)
            if lookingFor == tempSet:
                temp = tuple(tempDict.itervalues())
                output = (key, temp)
                outSet.add(output)
                break

    output_vals = []
    for key, event_tuple in outSet:
        output_val = TimedEvent(
            event_id=key[0],
            timed_templates=list(event_tuple))
        output_vals.append(output_val)
    return output_vals


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


def event_eval_rdd(sc, rdd_log_lines, event_list,
                 window_length=120):
    '''
    Performs the event generation from incoming DistributedLogLine rdd

    Args:
        sc(sparkContext):
        rdd_log_lines(DistributedLogLines): rdd of DistributedLogLines created
        by earlier processing
        event_list(list(Event)): List of event definitions
        window_length(int): window length to evaluate events in (seconds)

    Returns:
        retval(rdd tuple(tuple(eventId,windowID),tuple(DistributedLogLines)))

    '''

    template2event, event2template = make_lookup_dicts(event_list)
    template2event_broadcast = sc.broadcast(template2event)
    event2template_broadcast = sc.broadcast(event2template)

    windowed = rdd_log_lines.map(lambda line: event_window(line, window_length))
    edist = windowed.flatMap(lambda line: ship_events(line, template2event_broadcast))
    eventloglist = edist.groupByKey()
    outEvents = eventloglist.flatMap(lambda line: make_events_from_lines(line,
                                                                      event2template_broadcast))

    return outEvents
