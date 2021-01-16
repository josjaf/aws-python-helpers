import logging
import os


def __init__(*args, **kwargs):
    return
def get_logger():
    log_level = str(os.environ.get('LOG_LEVEL')).upper()
    if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        log_level = 'INFO'
    logger = logging.getLogger()
    #logging.basicConfig(level=logging.DEBUG)
    logger.setLevel(log_level)
    logger = logging.getLogger(__name__)
    return logger


def get_logger_v2():

    import logging

    # Initialize you log configuration using the base class
    logging.basicConfig(level = logging.INFO)

    # Retrieve the logger instance
    logger = logging.getLogger()

    # Log your output to the retrieved logger instance
    logger.info("Python for the win!")

    return logger

def get_logger_v21():

    import logging
    logging.getLogger().setLevel(logging.INFO)
    if logging.getLogger().hasHandlers():
        # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
        # `.basicConfig` does not execute. Thus we set the level directly.
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    return logger