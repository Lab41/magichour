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
    return random.sample(objs, max(1, int(ratio*len(objs))))

def mean(l):
    return sum(l) / float(len(l))

def logline_distance(logline1, logline2):
    return distance.levenshtein(logline1.text.strip().split(), logline2.text.strip().split())

def mean_distance(point, points, distance_fn=logline_distance):
    pts = list(points)
    if not pts:
        return 0
    distances = [distance_fn(point, other_point) for other_point in pts]
    return mean(distances)

def one_to_others_iter(values):
    for idx in xrange(len(values)):
        mask = [1]*len(values)
        mask[idx] = 0
        cur_value = values[idx]
        others = itertools.compress(values, mask) #list(itertools.compress(values, mask))
        yield (cur_value, others)

def silhouette_coefficient(val, same_cluster_vals, closest_cluster_vals):
    """
    The Silhouette Coefficient is defined for each sample and is composed of two scores:
        a: The mean distance between a sample and all other points in the same class.
        b: The mean distance between a sample and all other points in the next nearest cluster.

    The Silhouette Coefficient s for a single sample is then given as:
        s = b - a / max(a, b)

    The score is bounded between -1 for incorrect clustering and +1 for highly dense clustering.
    Scores around zero indicate overlapping clusters.
    The score is higher when clusters are dense and well separated, which relates to a standard concept of a cluster.
    The Silhouette Coefficient is generally higher for convex clusters than other concepts of clusters,
        such as density based clusters like those obtained through DBSCAN.

    See http://scikit-learn.org/stable/modules/clustering.html#silhouette-coefficient for more details.

    Args:
        val: the value for which to calculate the silhouette coefficient
        same_cluster_vals: list of other values in the same cluster as val
        closest_cluster_vals: list of values in the closest other cluster to val

    Returns:
        s: the silhouette coefficient for val
    """
    a = mean_distance(val, same_cluster_vals)
    b = mean_distance(val, closest_cluster_vals)
    try:
        s = (b - a) / max(a, b)
        return s
    except ZeroDivisionError as zde:
        logger.info("A: %s, B: %s", str(a), str(b))
        logger.error("Val: %s", str(val))
        logger.error("Same cluster: %s", str(same_cluster_vals))
        logger.error("Closest cluster: %s", str(closest_cluster_vals))
        raise zde

def cluster_silhouette_coefficient(cluster, data_dict, closest_cluster_map,
                                   cluster_sample_ratio=None, cluster_sampling_seed=None,
                                   closest_cluster_sample_ratio=None, closest_cluster_sampling_seed=None):
    scores = []

    if cluster_sample_ratio:
        cluster = sample(cluster, cluster_sample_ratio, cluster_sampling_seed)

    #logger.info("Cluster size: %s..." % len(cluster))

    for val, others in one_to_others_iter(cluster):
        closest_cluster_vals = data_dict[closest_cluster_map[val.processed]]

        if closest_cluster_sample_ratio:
            closest_cluster_vals = sample(closest_cluster_vals, closest_cluster_sample_ratio, closest_cluster_sampling_seed)

        #logger.info("Closest cluster size: %s..." % len(closest_cluster_vals))

        s = silhouette_coefficient(val, others, closest_cluster_vals)
        scores.append(s)
    return scores

def multicluster_silhouette_coefficient(data_dict, closest_cluster_map, multicluster_sample_ratio=None, multicluster_sampling_seed=None, *args, **kwargs):
    coefficients = []
    keys_to_use = data_dict.keys()

    if multicluster_sample_ratio:
        keys_to_use = sample(data_dict.keys(), multicluster_sample_ratio, multicluster_sampling_seed)

    logger.info("Processing %s clusters..." % len(keys_to_use))

    for key in keys_to_use:
        values = data_dict[key]
        #logger.info("Processing cluster %s..." % (key))
        silhouette = cluster_silhouette_coefficient(values, data_dict, closest_cluster_map, *args, **kwargs)
        coefficients.extend(silhouette)
    return coefficients

def validate_templates(data_dict, closest_cluster_map, junk_drawer,
                       multicluster_sample_ratio=None, multicluster_sampling_seed=None,
                       cluster_sample_ratio=None, cluster_sampling_seed=None,
                       closest_cluster_sample_ratio=None, closest_cluster_sampling_seed=None,
                       jd_cluster_sample_ratio=None, jd_cluster_sampling_seed=None,
                       jd_closest_cluster_sample_ratio=None, jd_closest_cluster_sampling_seed=None):
    """
    Calculates a performance metric for the results of template generation.
    Higher performance metrics are desirable.

    Args:
        data_dict: mapping from template_id to list of original logline messages representing a cluster grouping
        closest_cluster_map: a map from a logline message to a template_id representing the next closest cluster
        junk_drawer: all logline messages which were mapped to template_id = -1

    Returns:
        The performance score, calculated as the mean of the silhouette coefficients of non-junk drawer entries
        and the inverse (i.e. multiplied by -1) silhouette coefficient of the junk drawer.
    """

    logger.info("Processing regular silhouettes...")
    silhouettes = multicluster_silhouette_coefficient(data_dict, closest_cluster_map,
                                                      multicluster_sample_ratio=multicluster_sample_ratio,
                                                      multicluster_sampling_seed=multicluster_sampling_seed,
                                                      cluster_sample_ratio=cluster_sample_ratio,
                                                      cluster_sampling_seed=cluster_sampling_seed,
                                                      closest_cluster_sample_ratio=closest_cluster_sample_ratio,
                                                      closest_cluster_sampling_seed=closest_cluster_sampling_seed)


    logger.info("Processing junk drawer silhouettes...")
    jd_silhouette = cluster_silhouette_coefficient(junk_drawer, data_dict, closest_cluster_map,
                                                   cluster_sample_ratio=jd_cluster_sample_ratio,
                                                   cluster_sampling_seed=jd_cluster_sampling_seed,
                                                   closest_cluster_sample_ratio=jd_closest_cluster_sample_ratio,
                                                   closest_cluster_sampling_seed=jd_closest_cluster_sampling_seed)


    # A lower silhouette coefficient for the junk drawer means that it is more dispersed (this is good!)
    # Multiply jd_silhouette by -1 because we are trying to maximize the template validation score.
    validation_score = mean(silhouettes)
    logger.info("Mean regular silhouette score: %s" % validation_score)
    jd_validation_score = mean(jd_silhouette)
    logger.info("Mean JD silhouette score: %s" % jd_validation_score)
    validation_score = mean(silhouettes + [(-1.0) * jd_validation_score])
    logger.info("Mean regular + JD silhouette score: %s" % validation_score)
    return validation_score


def validation_distribution(eval_loglines, gen_templates, iterations, sampling_ratio=None, sampling_seed=None, *args, **kwargs):
    scores = []
    orig_eval_loglines = eval_loglines
    orig_gen_templates = gen_templates

    for x in xrange(iterations):
        logger.info("Running iteration %s..." % str(x+1))

        if sampling_ratio:
            eval_loglines = sample(orig_eval_loglines, sampling_ratio, sampling_seed)
            relevant_templates = set([eval_logline.templateId for eval_logline in eval_loglines])
            gen_templates = [template for template in orig_gen_templates if template.id in relevant_templates]
            logger.info("Sampled %s of %s loglines." % (len(eval_loglines), len(orig_eval_loglines)))

        logger.info("Creating data dictionary and junk drawer...")
        data_dict, junk_drawer = get_data_dict(eval_loglines)

        logger.info("Creating closest cluster map...")
        closest_cluster_map = find_closest_templates(eval_loglines, gen_templates)

        logger.info("Calling validate_templates()...")
        score = validate_templates(data_dict, closest_cluster_map, junk_drawer, *args, **kwargs)

        scores.append(score)
        logger.info("Score: %s" % score)
    np_scores = np.array(scores)
    m = np_scores.mean()
    std = np_scores.std()
    logger.info("Mean: %s, Stdev: %s" % (m, std))
    return (m, std)

###

def closest_template_dist(logline, template, distance_fn=distance.levenshtein):
    return distance_fn(logline.processed.strip().split(), template.raw_str.strip().split())

def find_closest_templates(eval_loglines, templates):
    closest_template_map = {}
    for eval_logline in eval_loglines:
        if eval_logline.processed not in closest_template_map:
            scores = sorted(templates, key=lambda template: closest_template_dist(eval_logline, template))

            # Store template id of the NEXT closest cluster
            next_closest_id = 1
            while eval_logline.templateId == scores[next_closest_id].id:
                #logger.info("INCREMENTING NEXT_CLOSEST_ID")
                next_closest_id += 1
            closest_template_map[eval_logline.processed] = scores[next_closest_id].id
    return closest_template_map

def get_data_dict(eval_loglines):
    data_dict = defaultdict(list)
    for eval_logline in eval_loglines:
        data_dict[eval_logline.templateId].append(eval_logline)

    if -1 in data_dict:
        junk_drawer = data_dict[-1]
        del data_dict[-1]
    else:
        junk_drawer = []

    return data_dict, junk_drawer