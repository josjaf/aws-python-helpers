from newport_helpers import log_helpers
import os
import logging
class NewportHelpers():
    """
    Super class for importing
    """

    def __init__(self, *args, **kwargs):

        log_level = str(os.environ.get('LOG_LEVEL')).upper()
        if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            log_level = 'INFO'

        log_format ='%(asctime)s %(message)s'
        log_format = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        datefmt='%m/%d/%Y %I:%M:%S %p'
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        print(f"Log Level: {log_level}")
        # logger.setLevel(level=log_level)
        # logger = logging.getLogger()
        logger = logging.getLogger(__name__)

        logging.getLogger().setLevel(level=log_level)

        if logging.getLogger().hasHandlers():
            # The Lambda environment pre-configures a handler logging to stderr. If a handler is already configured,
            # `.basicConfig` does not execute. Thus we set the level directly.
            logging.getLogger().setLevel(level=log_level)
        else:
            logging.basicConfig(level=log_level, format=log_format, datefmt=datefmt)
            # logging.basicConfig(level=log_level)


            # logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger()
        #### Supress botocore logs
        logging.getLogger('botocore').setLevel(logging.WARNING)
        self.logger = logger


nph = NewportHelpers()



