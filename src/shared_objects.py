import os
import sys
import json
import datetime as dt
import logging
from logging.handlers import TimedRotatingFileHandler


config = None
root = None
log = None


def trace(self, message, *args, **kws):
    if self.isEnabledFor(5):
        self._log(5, message, args, **kws)


def get_level_number(level):
    return {
        'trace': 5,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
    }.get(level.lower(), logging.INFO)


def get_level_name(level):
    return {
        5: 'trace',
        logging.DEBUG: 'debug',
        logging.INFO: 'info',
        logging.WARNING: 'warning',
        logging.ERROR: 'error',
        logging.CRITICAL: 'critical',
    }.get(level, "unknown")


def human_size(bsize, units=[' bytes','KB','MB','GB','TB', 'PB', 'EB']):
    """ Returns a human readable string representation of bytes """
    return str(bsize) + units[0] if bsize < 1024 else human_size(bsize >> 10, units[1:])


def absolute_path(cfg):
    global root
    global log
    for key in cfg:
        if key == 'path':
            new_path = os.path.join(root, cfg[key])
            log.trace("translating config object key {} from {} to {}".format(key, cfg[key], new_path))
            cfg[key] = new_path
    return cfg


def relative_path(path):
    global root
    return os.path.join(root, path)


def init(config_file_path):
    global config
    global log
    global root
    # define root path
    root = os.path.dirname(os.path.abspath(__file__))
    # parse config
    with open(os.path.join(root, config_file_path)) as json_file:
        config = json.load(json_file)
    # add log level
    logging.TRACE = 5  # between NOSET and DEBUG
    logging.addLevelName(logging.TRACE, "TRACE")
    logging.Logger.trace = trace
    log = logging.getLogger('LABMAN')
    # set default level
    log.setLevel(get_level_number(config["logger"]["level"]))
    # create file handler which logs even debug messages
    fh = TimedRotatingFileHandler(os.path.join(root, config["logger"]["logDirectory"], config["logger"]["logFile"]),
                                  when="midnight")
    # fh = TimedRotatingFileHandler(os.path.join(config["logger"]["logDirectory"], config["logger"]["logFile"]),
    #                               when="D", backupCount=1000)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(module)s][%(funcName)s:%(lineno)d] %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)
    log.info("****************************************")
    log.info("*** Started logging with level {} ***".format(logging.getLevelName(log.getEffectiveLevel())))
    log.info("****************************************")
