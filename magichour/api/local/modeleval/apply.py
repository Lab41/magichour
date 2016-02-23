import functools
import re
import multiprocessing
import json
from operator import attrgetter
from collections import defaultdict, Counter
from functools import partial
from multiprocessing import Pool

from magichour.api.local.util.log import get_logger
from magichour.api.local.util.namedtuples import TimedEvent, DistributedLogLine
logger = get_logger(__name__)


def templates_2_freqwords(templates):
    '''
    Creates a frequent word list from templates
    Args:
        templates (list(DistributedTemplateLine)): List of input templates

    Returns:
        freq_words (set(str)): Set of frequent words
    '''
    skip = re.compile(r'\*\{\d+,\d+\}')
    freq_words = set()
    for template in templates:
        for word in template.raw_str.split():
            if word.startswith('*') and skip.match(word):
                pass
            else:
                freq_words.add(word)
    return freq_words


def template_2_template_dict(templates, freq_words):
    template_dict = {}
    for template in templates:
        pattern = tuple(
            [word for word in template.raw_str.split() if word in freq_words])
        template_dict[pattern] = template
    return template_dict


def process_line_fast(
        logline,
        template_dict_maybe_bcast=None,
        freq_words_maybe_bcast=None):
    # If distributed version then unwrap broadcast variable
    if isinstance(
            template_dict_maybe_bcast,
            dict) or isinstance(
            template_dict_maybe_bcast,
            set):
        template_dict = template_dict_maybe_bcast
        freq_words = freq_words_maybe_bcast
    else:
        template_dict = template_dict_maybe_bcast.value
        freq_words = freq_words_maybe_bcast.value

    # Extract frequent words in order and make tuple so it is hashable
    logline_pattern = tuple(
        [word for word in logline.processed.split() if word in freq_words])

    if logline_pattern in template_dict:
        template = template_dict[logline_pattern]

        template_replacement_dict = defaultdict(list)

        if len(template.skip_words) > 0:
            skip_found = template.template.search(logline.processed)
            if skip_found:
                for i in range(len(template.skip_words)):
                    template_replacement_dict[template.skip_words[i]]\
                        .append(skip_found.groups()[i])

        return DistributedLogLine(ts=logline.ts,
                                  text=logline.text,
                                  processed=logline.processed,
                                  proc_dict=logline.proc_dict,
                                  template=template.template.pattern,
                                  templateId=template.id,
                                  template_dict=template_replacement_dict)
    else:
        # could not find a template match
        return DistributedLogLine(ts=logline.ts,
                                  text=logline.text,
                                  processed=logline.processed,
                                  proc_dict=logline.proc_dict,
                                  template=None,
                                  templateId=-1,
                                  template_dict=None)


re_type = re.compile(r'type=(\S+)')


def process_auditd_line(logline, templates):
    audit_msg_type = re_type.search(logline.text)
    if not audit_msg_type:
        raise ValueError(
            'Does not match expected auditd format; missing type=TYPE: %s' %
            logline.text)

    audit_msg_type = audit_msg_type.group(1)
    if audit_msg_type not in templates:
        raise KeyError("type=%s not in dictionary" % audit_msg_type)

    # return TimedTemplate(logline.ts, templates[audit_msg_type], logline.id)

    return DistributedLogLine(
        ts=logline.ts,
        text=logline.text,
        processed=logline.processed,
        proc_dict=logline.proc_dict,
        template=None,
        templateId=templates[audit_msg_type],
        template_dict=None,
    )


def apply_templates(
        templates,
        loglines,
        mp=True,
        type_template_auditd=False,
        **kwargs):
    """
    Applies the templates on an iterable. This function creates a list of TimedTemplate named tuples.
    In effect this will produce a list of which templates occurred at which times.
    -1 is the template_id that is used for a logline which was unable to be matched to a template.

    The templates accepted by this function is exactly the output of functions in template.py
    This function has the option of running in either multiprocessing mode (mp=True by default) or not.

    Args:
        templates: iterable Templates to apply
        loglines: loglines which will be examined

    Kwargs:
        mp: whether or not to run in multiprocessing mode (default: True)
        type_template_auditd: whether or not to use specialized auditd type template processing (default: False)

    Returns:
        timed_templates: a list of TimedTemplate named tuples that represent which templates occurred at which times in the log file.

    """

    # Change processing mode for auditd data by Templating based on type=TYPE
    if type_template_auditd:
        process_function = process_auditd_line
    else:
        freq_words = templates_2_freqwords(templates)
        template_dict = template_2_template_dict(templates, freq_words)
        if not freq_words:
            raise ValueError('freq words should be set')
        # (logline, template_dict_maybe_bcast, freq_words_maybe_bcast)#process_line
        process_function = process_line_fast

    if mp:
        # Use multiprocessing.Pool to use multiple CPUs
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        if freq_words:
            f = functools.partial(process_function,
                                  template_dict_maybe_bcast=template_dict,
                                  freq_words_maybe_bcast=freq_words)
        else:
            f = functools.partial(process_function, templates)
        processed_loglines = pool.map(func=f, iterable=loglines)
    else:
        # Do this the naive way with one CPU
        processed_loglines = []
        for logline in loglines:
            if freq_words:
                processed_loglines.append(
                    process_function(
                        logline,
                        template_dict,
                        freq_words))
            else:
                processed_loglines.append(process_function(logline, templates))
    return processed_loglines


#####

def count_templates(timed_templates):
    counts = defaultdict(int)
    for timed_template in timed_templates:
        counts[timed_template.template_id] += 1
    return counts


def make_t2e(events):
    t2e = defaultdict(set)
    for event in events:
        for template_id in sorted(event.template_ids):
            t2e[template_id].add(event.id)
    return t2e


def create_queues(events, log_lines):
    template2event = make_t2e(events)

    event_template_streams = defaultdict(list)
    for log_line in log_lines:
        for event_id in template2event[log_line.templateId]:
            event_template_streams[event_id].append(log_line)

    return event_template_streams


def jaccard(s1, s2):
    return len(s1 & s2) / float(len(s1 | s2))


def get_inner_list_vals(d):
    d_vals = set()
    for d_val_list in d.itervalues():
        d_vals.update(d_val_list)
    return d_vals


def jaccard_dicts(d1, d2, key_weight=0.0):
    jaccard_keys = jaccard(d1.viewkeys(), d2.viewkeys())
    d1_vals = get_inner_list_vals(d1)
    d2_vals = get_inner_list_vals(d2)
    jaccard_vals = jaccard(d1_vals, d2_vals)
    return (jaccard_keys * key_weight) + (jaccard_vals * (1 - key_weight))


def calc_similarity(msg1, msg2):
    """
    Similarity between candidate and original: weighted Jaccard similarity between replacement keys and values
        1.0 = identical (best/greatest similarity)
        0.0 = nothing in common

    Returns: 0 <= similarity <= 1
    """
    # TODO: Look at handling case when dict is a json dict
    # TODO: Look at adding tempalte_dict to proc_dict
    candidate = msg1.proc_dict
    orig = msg2.proc_dict
    return jaccard_dicts(candidate, orig) if candidate and orig and len(
        candidate) > 0 and len(orig) > 0 else 0


def get_start_index(idx, log_msgs, start_time):
    """
    Function that searches for the index of the log message that is just before the start_time (starting from idx)
    Args:
        idx (int): Index to start from
        log_msgs (list(DistributedLogLines)): List of messages to process
        start_time (float): The start time to search for

    Returns:
        idx (int): The index that is just before the start_time (or the start)
    """
    while idx >0 and log_msgs[idx-1].ts >= start_time:
        idx -= 1
    return idx


def get_end_index(idx, log_msgs, end_time):
    """
    Function that searches for the index of the log message that is just after the end_time (starting from idx)
    Args:
        idx (int): Index to start from
        log_msgs (list(DistributedLogLines)): List of messages to process
        end_time (float): The end time to search for

    Returns:
        idx (int): The index that is just after the end_time (or the end)
    """
    while idx < len(log_msgs) - 1 and log_msgs[idx].ts <= end_time:
        idx += 1
    return idx


def create_window_around_id(idx, log_msgs, window_time):
    """
    Find the start/stop index around a specific log message that defines a window of +/- window_time
    Args:
        idx (int): Index of the message to use as the center
        log_msgs (list(DistributedLogLines)): List of messages to process
        window_time (int): The amount of time +/- to search

    Returns:
        tuple(start_idx, end_idx): The start and end indexes that define the window
    """
    id_time = log_msgs[idx].ts
    start_time = id_time - window_time
    start_idx = get_start_index(idx, log_msgs, start_time)

    end_time = id_time + window_time
    end_idx = get_end_index(idx, log_msgs, end_time)
    return (start_idx, end_idx)


def get_similarity(idx1, idx2, log_msgs):
    """
    Helper function in getting similarity between two log messages by comparing their dictionary content.
    This function extracts the two relevant messages and passes them to calc_similarity
    Args:
        idx1 (int): Index of 1st message to compare
        idx2 (int): Index of 2nd message to compare

    Returns:
        similarity (float): The jaccard similarity of the contents of the two dictionaries
    """
    msg1 = log_msgs[idx1]
    msg2 = log_msgs[idx2]
    return calc_similarity(msg1, msg2)


def apply_queue(event, log_msgs, window_time=60):
    """
    The main function responsible for taking a single event and a list of messages and finding the
    occurrences of that event in the data

    Note: Assumes that log_msgs only contains template_ids in event

    Args:
        event (Event): The event definition to look for
        log_msgs (list(DistributedLogLine)): A list of messages to look for the event in
        window_time (int): All templates in an event must occur within this time. Note: actually specified as the
                            distance from the least likely template [not a strict limit on event length]
    Returns:
        timed_events (list(TimedEvent)): A list of found events with their component log lines
    """
    # The rest of the processing assumes that log messages are in time order
    log_msgs = sorted(log_msgs, key=attrgetter('ts'))

    id_counts = Counter(
        [log_msg.templateId for log_msg in log_msgs]).most_common()
    id_counts = [template_id for (template_id, count) in reversed(id_counts)]

    # id_counts.most_common()[-1][0] # Just keep id, drop count
    least_common_template_id = id_counts[0]

    timed_events = []
    idx_used = set()
    for idx, log_msg in enumerate(log_msgs):
        if log_msg.templateId == least_common_template_id:
            # Get window around anchor msg
            (start_idx, end_idx) = create_window_around_id(
                idx, log_msgs, window_time)

            # Figure out what template IDs/in what counts are present
            template_id_to_idx = defaultdict(list)
            for i in range(start_idx, end_idx + 1):
                if i not in idx_used:
                    template_id_to_idx[log_msgs[i].templateId].append(i)

            # If we have everything we need to make a match
            if len(template_id_to_idx) != len(event.template_ids):
                logger.debug(
                    'Not all templates present. Found %d of %d' %
                    (len(template_id_to_idx), len(
                        event.template_ids)))
            else:
                # Add current id
                idx_in_event = set([idx])

                # iterate through component template_ids adding the best one to
                # each event
                for template_id in id_counts[1:]:
                    # If there's only one of that template ID in this window
                    # then that's what goes in our event
                    if len(template_id_to_idx[template_id]) == 1:
                        idx_in_event.add(template_id_to_idx[template_id][0])
                    elif len(template_id_to_idx[template_id]) > 1:
                        id_sim = []
                        for candidate_index in template_id_to_idx[template_id]:
                            sim = get_similarity(
                                idx, candidate_index, log_msgs)
                            delta_t = abs(
                                log_msgs[idx].ts - log_msgs[candidate_index].ts)
                            id_sim.append(
                                (-abs(sim), delta_t, candidate_index))

                        id_sim = sorted(id_sim)
                        # Pulll 3rd field from 1st item
                        idx_in_event.add(id_sim[0][2])
                    else:
                        # Should be unreachable
                        raise ValueError('Not sure how we got here...')
                if len(idx_in_event) == len(event.template_ids):
                    te = TimedEvent(
                        event_id=event.id, timed_templates=[
                            log_msgs[selected_idx] for selected_idx in idx_in_event])
                    timed_events.append(te)
                    idx_used.update(idx_in_event)
                else:
                    logger.warn('Should never have reached this point')

    return timed_events


def apply_single_tuple(input_tuple, window_time=None):
    """
    Helper function that takes a tuple as input and breaks out inputs to pass
    to apply_queue
    Args:
        input_tuple(tuple(Event, list(DistributedLogLines))): A tuple of inputs to be split and passed
    Returns:
        timed_events (list(TimedEvent)): A list of found events with their component log lines
    """
    event, log_msgs = input_tuple
    return apply_queue(event, log_msgs, window_time=window_time)


def apply_events(events, log_msgs, window_time=60, mp=False):
    """
    Main entry point for local processing to apply events. The processing takes a list of timed templates
    as input and reorganizes the list into a dictionary of lists where each list contains all the templates
    relevant to a given event (done in create_queues). That input then allows us to parallelize looking
    for a given event in some subset of the events.

    Distributed processing bypasses this function and call aply_single_tuple directly

    Args:
        events (list(Event)): The list of events to search for in the log messages
        log_msgs (list(DistributedLogLine)): A list of distributed log lines to look for events in
        window_time (int): All templates in an event must occur within this time. Note: actually specified as the
                            distance from the least likely template [not a strict limit on event length]
        mp (Bool): Whether to use a multiprocessing pool to parallelize processing
    Returns:
        timed_events (list(TimedEvent)): A list of found events with their component log lines
    """
    queues = create_queues(events, log_msgs)
    event_dict = {event.id:event for event in events}

    def apply_single_tuple_generator(events, queues):
        """
        Generator to allow us to not materialize entire list of tuples at once
        """
        for idx in sorted(queues.keys()):
            yield (events[idx], queues[idx])

    # Helper function to allow only one arg to apply_single_tuple
    apply_w_defaults = partial(apply_single_tuple, window_time=window_time)

    if mp:
        # Use multiprocessing pool to process in parallel
        logger.info('Using multiprocessing to apply events')
        p = Pool()  # Note: must define pool after functions
        timed_events = p.map(
            apply_w_defaults,
            apply_single_tuple_generator(
                event_dict,
                queues))
    else:
        # Single threaded processing
        logger.info('Using single-thread to apply events')
        timed_events = []
        for idx, input_tuple in enumerate(
            apply_single_tuple_generator(
                event_dict, queues)):
            try:
                if idx % 10 == 0:
                    logger.info(
                        'Processing event %d of %d' %
                        (idx, len(event_dict)))
                idx_timed_events = apply_w_defaults(input_tuple)
                timed_events.extend(idx_timed_events)
            except:
                logger.error('Failure on event: %s' % str(input_tuple[0]))
                raise
    return timed_events
