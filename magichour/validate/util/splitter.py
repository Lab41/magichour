from random import shuffle


def splitRDD(rdd, weights=[0.8, 0.1, 0.1]):
    train, validation, test = rdd.randomSplit(weights=weights)
    return train, validation, test


def split(data, weights=[0.8, 0.1, 0.1]):
    d = [x for x in data]
    shuffle(d)
    idx_train = len(d) * weights[0]
    idx_validation = len(d) * (weights[0] + weights[1])
    train = d[:idx_train]
    validation = d[idx_train:idx_validation]
    test = d[idx_validation:]
    return train, validation, test
