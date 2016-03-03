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


def inter_intra_dists(val, same_cluster_vals, closest_cluster_vals):
    a = mean_distance(val, same_cluster_vals) # mean intracluster distance
    b = mean_distance(val, closest_cluster_vals) # mean intercluster distance
    return (a, b)


def get_closest_template(eval_logline, data_dict, closest_cluster_map):
    dists, templates = zip(*closest_cluster_map[eval_logline.processed])
    closest_template = next((template for template in templates if template.id in data_dict.keys()), None)
    return closest_template


def cluster_dists(cluster, data_dict, closest_cluster_map):
    intra_scores = []
    inter_scores = []

    for val, others in one_to_others_iter(cluster):
        closest_template = get_closest_template(val, data_dict, closest_cluster_map)
        # use map to find the closest_cluster, then get all values from that cluster
        closest_cluster_vals = data_dict[closest_template.id]

        intra, inter = inter_intra_dists(val, others, closest_cluster_vals)
        intra_scores.append(intra)
        inter_scores.append(inter)
    return (mean(intra_scores), mean(inter_scores))


def multicluster_dists(data_dict, closest_cluster_map):
    intra_scores = []
    inter_scores = []
    keys_to_use = data_dict.keys()

    logger.info("Processing %s clusters..." % len(keys_to_use))

    for key in keys_to_use:
        cluster = data_dict[key]
        mean_intra, mean_inter = cluster_dists(cluster, data_dict, closest_cluster_map)
        intra_scores.append(mean_intra)
        inter_scores.append(mean_inter)
    return (mean(intra_scores), mean(inter_scores))


def validate_templates(data_dict, closest_cluster_map, junk_drawer):
    logger.info("Processing regular clusters...")
    mean_intra, mean_inter = multicluster_dists(data_dict, closest_cluster_map)

    logger.info("Processing junk drawer...")
    mean_jd_intra, mean_jd_inter = cluster_dists(junk_drawer, data_dict, closest_cluster_map)

    return (mean_intra, mean_inter, mean_jd_intra, mean_jd_inter)


def dist_stats(arr):
    np_arr = np.array(arr)
    return (np_arr.mean(), np_arr.std())


def validation_sample(eval_loglines, gen_templates, iterations, sampling_ratio=None, sampling_seed=None):
    sample_mean_intras = []
    sample_mean_inters = []
    sample_mean_jd_intra = []
    sample_mean_jd_inter = []

    orig_eval_loglines = eval_loglines
    orig_gen_templates = gen_templates

    #logger.info("Creating closest cluster map... (eval_loglines = %s, gen_templates = %s)" % (eval_loglines, gen_templates))
    #closest_cluster_map = find_closest_templates(eval_loglines, gen_templates)

    for itr in xrange(1, iterations+1):
        logger.info("Running iteration %s..." % str(itr))

        if sampling_ratio:
            eval_loglines = sample(orig_eval_loglines, sampling_ratio, sampling_seed)
            relevant_templates = set([eval_logline.templateId for eval_logline in eval_loglines])
            gen_templates = [template for template in orig_gen_templates if template.id in relevant_templates]
            logger.info("Sampled %s of %s loglines." % (len(eval_loglines), len(orig_eval_loglines)))

        logger.info("Creating data dictionary and junk drawer...")
        data_dict, junk_drawer = get_data_dict_and_jd(eval_loglines)

        logger.info("Creating closest cluster map...")
        closest_cluster_map = find_closest_templates(eval_loglines, gen_templates)

        logger.info("Calling validate_templates()...")
        mean_intra, mean_inter, mean_jd_intra, mean_jd_inter = validate_templates(data_dict, closest_cluster_map, junk_drawer)

        sample_mean_intras.append(mean_intra)
        sample_mean_inters.append(mean_inter)
        sample_mean_jd_intra.append(mean_jd_intra)
        sample_mean_jd_inter.append(mean_jd_inter)

    return (dist_stats(sample_mean_intras),
            dist_stats(sample_mean_inters),
            dist_stats(sample_mean_jd_intra),
            dist_stats(sample_mean_jd_inter))

###


def closest_template_dist(logline, template, distance_fn=distance.nlevenshtein):
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
