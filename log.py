'''Sets up a logging

'''
import json
import logging
import datetime
import pathlib

def get_logger(file_level = logging.INFO, term_level = logging.INFO):

    datefmt = '%Y-%m-%d %H:%M:%S'
    msecfmt = '%s.%03d'
    format_str = '%(asctime)s %(levelname)-8s; %(message)s'

    now = datetime.datetime.now()
    datetime_str = now.strftime("%Y-%m-%d_at_%H-%M")

    logger = logging.getLogger('SSTServer')
    logger.setLevel(logging.DEBUG)

    path = pathlib.Path(__file__).parent / 'logs'

    log_fname = path / f'SSTServer_{datetime_str}.log'

    if file_level is not None:
        fh = logging.FileHandler(log_fname)
        fh.setLevel(file_level) #debug and worse
        form_fh = logging.Formatter(format_str)
        form_fh.default_time_format = datefmt
        form_fh.default_msec_format = msecfmt
        fh.setFormatter(form_fh)
        logger.addHandler(fh)

    if term_level is not None:
        ch = logging.StreamHandler()
        ch.setLevel(term_level)
        form_ch = logging.Formatter(format_str)
        form_ch.default_time_format = datefmt
        form_ch.default_msec_format = msecfmt
        ch.setFormatter(form_ch)
        logger.addHandler(ch)

    return logger