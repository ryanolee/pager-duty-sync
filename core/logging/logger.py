import logging

def get_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger
