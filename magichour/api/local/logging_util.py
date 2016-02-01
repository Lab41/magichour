from collections import namedtuple
import logging
import time

reload(logging)

# Disables this logging level + all levels below.
# Set to None if you want to enable all logging.
# Set to logging.CRITICAL if you want to disable all logging.
DISABLE_LOGGING_LEVEL = logging.DEBUG  # logging.CRITICAL

HandlerInfo = namedtuple("HandlerInfo", ["handler", "level", "formatter"])
loggers = {}

def run_once(f):
    def wrapper(*args, **kwargs):
        if not f.has_run:
            f.has_run = True
            return f(*args, **kwargs)
    f.has_run = False
    return wrapper
    
@run_once
def disable_logging(level=None):
    if level:
        logging.disable(level)

def get_logger(name, level=logging.INFO, handler_infos=None):
    disable_logging(DISABLE_LOGGING_LEVEL) 

    if name in loggers:
        return loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Default logger handler specification goes here.
    if not handler_infos:
        handler = logging.StreamHandler()
        format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
        handler_infos = [HandlerInfo(handler, level, format)]

    for handler, level, format in handler_infos:
        formatter = logging.Formatter(format)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    loggers[name] = logger
    return logger

def log_exc(logger, msg, exc_type=Exception):
    logger.error(msg)
    raise exc_type(msg)

logger = get_logger(__name__)

# Stick this as a decorator on any function to print the # of time spent in that function.
def log_time(f):
    def wrapper(*args, **kwargs):
        tstart = time.time()
        result = f(*args, **kwargs)
        m, s = divmod(time.time()-tstart, 60)
        msg = "Time in %s(): "
        if m == 0:
            logger.info(msg+"%s seconds", f.__name__, s)
        else:
            logger.info(msg+"%s minutes, %s seconds", f.__name__, m, s)
        return result
    return wrapper
