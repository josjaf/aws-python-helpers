import logging
import os

class LogHeloers():
    def __init__(self, *args, **kwargs):
        return
    def get_logger(self):
        log_level = str(os.environ.get('LOG_LEVEL')).upper()
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            log_level = 'INFO'
        logger = logging.getLogger()
        #logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(log_level)
        logger = logging.getLogger(__name__)
        return logger


