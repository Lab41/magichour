import math

from magichour.api.local.util.log import log_time


def tf(elem, elems):
    return list(elems).count(elem) / len(elems)


def idf(elem, elemss):
    def num_containing():
        return sum(1 for elems in elemss if elem in elems)
    return math.log(len(elemss) / num_containing())


def tf_idf(elem, elems, elemss):
    return tf(elem, elems)*idf(elem, elemss)


def tf_idf_filter(elemss, threshold):
    new_elemss = []
    for elems in elemss:
        new_elems = []
        for elem in elems:
            score = idf(elem, elemss) # tf_idf(elem, elems, elemss)
            if score > threshold:
                new_elems.append(elem)
        new_elemss.append(new_elems)
    return new_elemss


@log_time
def tfidf_filter_namedtuple(ntuples, threshold, ntuple_type):
    template_ids = [[template_id for template_id in ntuple.template_ids] for ntuple in ntuples]
    filtered = tf_idf_filter(template_ids, threshold)
    try:
        ret = [ntuple_type(ntuple.id, filtered_ids) for ntuple, filtered_ids in zip(ntuples, filtered) if filtered_ids]
    except AttributeError as ae:
        ret = [ntuple_type(filtered_ids) for filtered_ids in filtered if filtered_ids]
    return ret