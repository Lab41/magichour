import cPickle as pickle

from magichour.api.local.util.log import get_logger

logger = get_logger(__name__)


def read_pickle_file(pickle_file):
    logger.info("Reading pickle file: %s", pickle_file)
    with open(pickle_file, 'rb') as pf:
        data = pickle.load(pf)
    return data


def write_pickle_file(data, pickle_file):
    logger.info("Writing data to pickle file: %s", pickle_file)
    with open(pickle_file, 'wb') as pf:
        pickle.dump(data, pf)
