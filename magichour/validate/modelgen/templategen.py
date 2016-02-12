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
