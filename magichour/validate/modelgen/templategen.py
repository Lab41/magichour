import distance
import itertools

def mean(l):
    return sum(l) / float(len(l))

def mean_distance(point, points, distance_fn=distance.levenshtein):
    return mean([distance_fn(point, other_point) for other_point in points])

def one_to_others_iter(values):
    for idx in xrange(len(values)):
        mask = [1]*len(values)
        mask[idx] = 0
        cur_value = values[idx]
        others = list(itertools.compress(values, mask))
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
    s = (b - a) / max(a, b)
    return s

def cluster_silhouette_coefficient(cluster, data_dict, closest_cluster_map):
    scores = []
    for val, others in one_to_others_iter(cluster):
        s = silhouette_coefficient(val, others, data_dict[closest_cluster_map[val]])
        scores.append(s)
    return scores

def multicluster_silhouette_coefficient(data_dict, closest_cluster_map):
    coefficients = []
    for key, values in data_dict.iteritems():
        coefficients.extend(cluster_silhouette_coefficient(values, data_dict, closest_cluster_map)
    return coefficients

def validate_templates(data_dict, closest_cluster_map, junk_drawer):
    silhouettes = multicluster_silhouette_coefficient(data_dict, closest_cluster_map)
    """
    A lower silhouette coefficient for the junk drawer means that it is more dispersed.
    Multiply jd_silhouette by -1 because we are trying to maximize the template validation score.
    """
    jd_silhouette = cluster_silhouette_coefficient(junk_drawer, data_dict, closest_cluster_map) * -1
    return mean(silhouettes + jd_silhouette)
