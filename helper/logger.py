import logging

class LoggerFactory:
    def __init__(self):
        self.logger = logging.getLogger('logger')

        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

logger = LoggerFactory()

def log_info(message):
    logger.logger.info(message)

def log_warning(message):
    logger.logger.warning(message)

def log_error(message):
    logger.logger.error(message)