import collections
import distance
import itertools
import numpy as np
import random

from magichour.api.local.util.log import get_logger
from collections import defaultdict

logger = get_logger(__name__)


def sample(objs, ratio, seed=None):
    if seed:
        random.seed(seed)
    return random.sample(objs, max(1, int(ratio * len(objs))))


def mean(l):
    return sum(l) / float(len(l))


def logline_distance(logline1, logline2):
    return distance.nlevenshtein(
        logline1.text.strip().split(),
        logline2.text.strip().split())


def mean_distance(point, points, distance_fn=logline_distance):
    pts = list(points)
    if not pts:
        return 0
    distances = [distance_fn(point, other_point) for other_point in pts]
    return mean(distances)


def one_to_others_iter(values):
    for idx in xrange(len(values)):
        mask = [1] * len(values)
        mask[idx] = 0
        cur_value = values[idx]
        # list(itertools.compress(values, mask))
        others = itertools.compress(values, mask)
        yield (cur_value, others)


def intracluster_dists(cluster):
    intra_scores = []
    for val, others in one_to_others_iter(cluster):
        intra = mean_distance(val, others)  # mean intracluster distance
        intra_scores.append(intra)
    return mean(intra_scores)


def multiintracluster_dists(data_dict):
    intra_scores = []
    keys_to_use = data_dict.keys()

    logger.info("Processing %s clusters..." % len(keys_to_use))

    for key in keys_to_use:
        cluster = data_dict[key]
        mean_intra = intracluster_dists(cluster)
        intra_scores.append(mean_intra)
    return mean(intra_scores)


def validate_intracluster(data_dict, junk_drawer):
    logger.info("Processing regular clusters...")
    mean_intra = multiintracluster_dists(data_dict)

    logger.info("Processing junk drawer...")
    mean_jd_intra = intracluster_dists(junk_drawer)

    return (mean_intra, mean_jd_intra)


def dist_stats(arr):
    np_arr = np.array(arr)
    return (np_arr.mean(), np_arr.std())


def template_distance(template1, template2):
    return distance.nlevenshtein(
        template1.raw_str.strip().split(),
        template2.raw_str.strip().split()
    )


def intercluster_dists(templates):
    inter_dists = []
    for cur_template, other_templates in one_to_others_iter(templates):
        results = [(template_distance(cur_template, other_template),
                    other_template) for other_template in other_templates]
        results = sorted(results, key=lambda r: r[0])  # sort by distance
        # take best one (i.e. distance to the closest template)
        best = results[0]
        inter_dists.append(best[0])
    return mean(inter_dists)


def validation_sample(
        eval_loglines,
        gen_templates,
        iterations,
        sampling_ratio=None,
        sampling_seed=None):
    sample_mean_intras = []
    sample_mean_jd_intra = []
    sample_mean_inters = []

    orig_eval_loglines = eval_loglines
    orig_gen_templates = gen_templates

    #logger.info("Creating closest cluster map... (eval_loglines = %s, gen_templates = %s)" % (eval_loglines, gen_templates))
    #closest_cluster_map = find_closest_templates(eval_loglines, gen_templates)

    for itr in xrange(1, iterations + 1):
        logger.info("Running iteration %s..." % str(itr))

        if sampling_ratio:
            eval_loglines = sample(
                orig_eval_loglines,
                sampling_ratio,
                sampling_seed)
            relevant_templates = set(
                [eval_logline.templateId for eval_logline in eval_loglines])
            gen_templates = [
                template for template in orig_gen_templates if template.id in relevant_templates]
            logger.info("Sampled %s of %s loglines." %
                        (len(eval_loglines), len(orig_eval_loglines)))

        logger.info("Calling intercluster_dists()...")
        mean_inter = intercluster_dists(gen_templates)

        logger.info("Creating data dictionary and junk drawer...")
        data_dict, junk_drawer = get_data_dict_and_jd(eval_loglines)

        logger.info("Calling validate_intracluster()...")
        mean_intra, mean_jd_intra = validate_intracluster(
            data_dict, junk_drawer)

        sample_mean_intras.append(mean_intra)
        sample_mean_jd_intra.append(mean_jd_intra)
        sample_mean_inters.append(mean_inter)

    return (dist_stats(sample_mean_intras),
            dist_stats(sample_mean_jd_intra),
            dist_stats(sample_mean_inters))

###


def closest_template_dist(
        logline,
        template,
        distance_fn=distance.nlevenshtein):
    return distance_fn(
        logline.processed.strip().split(),
        template.raw_str.strip().split())


def find_closest_templates(eval_loglines, templates):
    closest_template_map = {}
    for eval_logline in eval_loglines:
        if eval_logline.processed not in closest_template_map:
            scores = []
            for template in templates:
                if eval_logline.templateId != template.id:
                    score = closest_template_dist(eval_logline, template)
                    scores.append((score, template))
            scores = sorted(scores, key=lambda x: x[0])
            closest_template_map[eval_logline.processed] = scores
    return closest_template_map


def get_data_dict_and_jd(eval_loglines):
    data_dict = defaultdict(list)
    for eval_logline in eval_loglines:
        data_dict[eval_logline.templateId].append(eval_logline)

    if -1 in data_dict:
        junk_drawer = data_dict[-1]
        del data_dict[-1]
    else:
        junk_drawer = []

    return data_dict, junk_drawer
