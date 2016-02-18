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


def process_line(templates, logline):
    for template in templates:
        skip_found = template.template.search(logline.processed)

        # TODO double check that the defaultdict is working as expected
        if skip_found:
            template_dict = defaultdict(list)

            for i in range(len(template.skip_words)):
                template_dict[
                    template.skip_words[i]].append(
                    skip_found.groups()[i])

            template_dict_str = json.dumps(template_dict) if template_dict else None

            return DistributedLogLine(ts=logline.ts,
                                      text=logline.text,
                                      processed=logline.processed,
                                      proc_dict=logline.proc_dict,
                                      template=template.template.pattern,
                                      templateId=template.id,
                                      template_dict=template_dict_str)

    # could not find a template match
    return DistributedLogLine(ts=logline.ts,
                              text=logline.text,
                              processed=logline.processed,
                              proc_dict=logline.proc_dict,
                              template=None,
                              templateId=-1,
                              template_dict=None)


re_type = re.compile(r'type=(\S+)')
def process_auditd_line(templates, logline):
    audit_msg_type = re_type.search(logline.text)
    if not audit_msg_type:
        raise ValueError('Does not match expected auditd format; missing type=TYPE: %s'%logline.text)

    audit_msg_type = audit_msg_type.group(1)
    if audit_msg_type not in templates:
        raise KeyError("type=%s not in dictionary"%audit_msg_type)

    #return TimedTemplate(logline.ts, templates[audit_msg_type], logline.id)

    return DistributedLogLine(
        ts=logline.ts,
        text=logline.text,
        processed=logline.processed,
        proc_dict=logline.proc_dict,
        template=None,
        templateId=templates[audit_msg_type],
        template_dict=None,
    )


def apply_templates(templates, loglines, mp=True, type_template_auditd=False, **kwargs):
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
        process_function = process_line

    if mp:
        # Use multiprocessing.Pool to use multiple CPUs
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        f = functools.partial(process_function, templates)

        processed_loglines = pool.map(func=f, iterable=loglines)
    else:
        # Do this the naive way with one CPU
        processed_loglines = []
        for logline in loglines:
            processed_loglines.append(process_function(templates, logline))
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
    d_vals = set()#[]
    for d_val_list in d.itervalues():
        d_vals.update(d_val_list)
        #for d_val in d_val_list:
        #    d_vals.append(d_val)
    return d_vals


def jaccard_dicts(d1, d2, key_weight=0.0):
    jaccard_keys = jaccard(d1.viewkeys(), d2.viewkeys())
    d1_vals = get_inner_list_vals(d1)
    d2_vals = get_inner_list_vals(d2)
    jaccard_vals = jaccard(d1_vals, d2_vals)
    return (jaccard_keys * key_weight) + (jaccard_vals * (1-key_weight))


def calc_similarity(msg1, msg2):
    """
    Similarity between candidate and original: weighted Jaccard similarity between replacement keys and values
        1.0 = identical (best/greatest similarity)
        0.0 = nothing in common

    Returns: 0 <= similarity <= 1
    """
    candidate = msg1.proc_dict
    orig = msg2.proc_dict
    return jaccard_dicts(candidate, orig) if candidate and orig and len(candidate) > 0 and len(orig) > 0 else 0


def get_start_index(idx, log_msgs, start_time):
    while log_msgs[idx].ts > start_time and idx != 0:
        idx -= 1
    return idx


def get_end_index(idx, log_msgs, end_time):
    while log_msgs[idx].ts < end_time and idx < len(log_msgs)-1:
        idx += 1
    return idx


def create_window_around_id(idx, log_msgs, window_time):
    id_time = log_msgs[idx].ts
    start_time = id_time - window_time
    start_idx = get_start_index(idx, log_msgs, start_time)

    end_time = id_time + window_time
    end_idx = get_end_index(idx, log_msgs, end_time)
    return (start_idx, end_idx)


def get_similarity(idx1, idx2, log_msgs):
    msg1 = log_msgs[idx1]
    msg2 = log_msgs[idx2]
    return calc_similarity(msg1, msg2)


def apply_queue(event, log_msgs, window_time=60):
    '''
    WARNING: Assumes that log_msgs only contains template_ids in event
    WARNING: Assumes that msgs are sorted
    '''
    id_counts = Counter([log_msg.templateId for log_msg in log_msgs]).most_common()
    id_counts = [template_id for (template_id, count) in reversed(id_counts)]

    least_common_template_id = id_counts[0] #id_counts.most_common()[-1][0] # Just keep id, drop count

    timed_events = []
    idx_used = set()
    for idx, log_msg in enumerate(log_msgs):
        if log_msg.templateId == least_common_template_id:
            # Get window around anchor msg
            (start_idx, end_idx) = create_window_around_id(idx, log_msgs, window_time)

            # Figure out what template IDs/in what counts are present
            template_id_to_idx = defaultdict(list)
            for i in range(start_idx, end_idx+1):
                if i not in idx_used:
                    template_id_to_idx[log_msgs[i].templateId].append(i)

            # If we have everything we need to make a match
            if len(template_id_to_idx) != len(event.template_ids):
                logger.debug('Not all templates present. Found %d of %d'%
                             (len(template_id_to_idx), len(event.template_ids )))
            else:
                # Add current id
                idx_in_event = set([idx])

                # iterate through component template_ids adding the best one to each event
                for template_id in id_counts[1:]:
                    # If there's only one of that template ID in this window then that's what goes in our event
                    if len(template_id_to_idx[template_id]) == 1:
                        idx_in_event.add(template_id_to_idx[template_id][0])
                    elif len(template_id_to_idx[template_id]) > 1:
                        id_sim = []
                        for candidate_index in template_id_to_idx[template_id]:
                            sim = get_similarity(idx, candidate_index, log_msgs)
                            delta_t = abs(log_msgs[idx].ts - log_msgs[candidate_index].ts)
                            id_sim.append((-abs(sim), delta_t, candidate_index))

                        id_sim = sorted(id_sim)
                        idx_in_event.add(id_sim[0][2]) # Pulll 3rd field from 1st item
                    else:
                        # Should be unreachable
                        raise ValueError('Not sure how we got here...')
                if len(idx_in_event) ==  len(event.template_ids):
                    te = TimedEvent(event_id=event.id,
                                timed_templates=[log_msgs[selected_idx] for selected_idx in idx_in_event])
                    timed_events.append(te)
                    idx_used.update(idx_in_event)
                else:
                    logger.warn('Should never have reached this point')

    return timed_events


def apply_single_tuple(input_tuple, window_time=None):
    event, queues = input_tuple
    queues = sorted(queues, key=attrgetter('ts'))
    return apply_queue(event, queues, window_time=window_time)


# assume timed_templates are ordered
def apply_events(events, timed_templates, window_time=60, mp=False):
    queues = create_queues(events, timed_templates)

    if mp:
        logger.info('Using multiprocessing to apply events')

        apply_w_defaults = partial(apply_single_tuple, window_time=window_time) #lambda x: apply_single_tuple(x, window_time=window_time)

        p = Pool() # Note: must define pool after functions
        timed_events = p.map(apply_w_defaults, [(events[idx], queues[idx]) for idx in sorted(queues.keys())])

    else:
        logger.info('Using single-thread to apply events')
        timed_events = []
        for idx in sorted(queues.keys()):
            try:
                if len(queues[idx]) > 0:
                    logger.info('Processing event %d of %d'%(idx, len(events)))
                    idx_timed_events = apply_queue(events[idx], sorted(queues[idx], key=attrgetter('ts')), window_time)
                    timed_events.extend(idx_timed_events)
            except:
                logger.error('Failure on idx: %d'%idx)
                raise
    return timed_events
