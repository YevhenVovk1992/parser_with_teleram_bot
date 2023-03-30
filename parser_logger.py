import logging
import os


class Logger:
    base_dir = os.path.dirname(__file__)
    log_path = base_dir + '/parser.log'
    logging.basicConfig(filename=log_path,
                        encoding='utf-8',
                        level=logging.INFO,
                        filemode='a',
                        format='%(asctime)s - %(levelname)s - %(message)s')

    @classmethod
    def console_logger(cls):
        """
        Custom logger which print message to the console
        """
        logger = logging.getLogger('__name__')
        level = logging.INFO
        logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        logger.addHandler(ch)
        return logger
