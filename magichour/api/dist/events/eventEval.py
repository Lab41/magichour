from collections import defaultdict


def eventWindow(line, windowLength):
    '''
    alias events to the same key based off time

    Args:
        line(DistributedLogLine):
        windowLength(int): Length in seconds of the window to apply

    Retval:
        retval(tuple(window,DistributedLogLine))
    '''
    key = (line.supportId, int(line.ts/windowLength))
    value = line
    return (key, value)


def shipEvents(line, t2e):
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


def makeEventsFromLines(line, e2t):
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
            tempDict[tList[inner].supportId] = tList[inner]
            tempSet.add(tList[inner].supportId)
            if lookingFor == tempSet:
                # print "FOUND:",tempSet
                temp = tuple(tempDict.itervalues())
                output = (key, temp)
                outSet.add(output)
                break
    # print "returning:",outSet
    return list(outSet)


def makeLookupDicts(eventdef):
    '''
    make the lookup dictionaries used for translating
    between templates and events which care about specific
    templates

    Args:
        eventdef(list(str)): list of templates which go together

    Returns:
        retval(tuple(defaultdict(set),defaultdict(set))):
            (templates->events, events->templates)
    '''
    template2event = defaultdict(set)
    event2template = defaultdict(set)

    for n, l in enumerate(eventdef):
        # print '******',n,l
        items = l.rstrip().lstrip().split()
        for i in items:
            # print n,i
            event2template[int(n)].add(int(i))

    for k, v in event2template.iteritems():
        for item in v:
            template2event[int(item)].add(int(k))

    return(template2event, event2template)


def eventEvalRDD(sc, rddlogLines, templateURI,
              windowLength=120):
    '''
    Performs the event generation from incomming DistributedLogLine rdd

    Args:
        sc(sparkContext):
        rddlogLines(DistributedLogLines): rdd of DistributedLogLines created
        by earlier processing 
        templateURI(str): URI to the file describing the event templates 
        each line of the file  is a space separated list of templates
        a specific event is sensitive to
        windowLength(int): window length to evaluate events in (seconds)

    Returns:
        retval(rdd tuple(tuple(eventId,windowID),tuple(DistributedLogLines)))

    '''
    temp = sc.textFile(templateURI)
    eventdef = temp.collect()

    t2e, e2t = makeLookupDicts(eventdef)
    t2e_B = sc.broadcast(t2e)
    e2t_B = sc.broadcast(e2t)

    windowed = rddlogLines.map(lambda line: eventWindow(line, windowLength))
    edist = windowed.flatMap(lambda line: shipEvents(line, t2e_B))
    eventloglist = edist.groupByKey()
    outEvents = eventloglist.flatMap(lambda line: makeEventsFromLines(line,
                                                                      e2t_B))

    return outEvents
