from collections import namedtuple
import logging

# Disables this logging level + all levels below.
# Set to None if you want to enable all logging.
# Set to logging.CRITICAL if you want to disable all logging.
DISABLE_LOGGING_LEVEL = None # logging.CRITICAL

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

def get_logger(name, level=logging.DEBUG, handler_infos=None):
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
