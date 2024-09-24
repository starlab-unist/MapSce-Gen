import logging

def get_logger(logger_name="", logger_level=logging.INFO):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level)
    
    formatter = logging.Formatter('%(levelname)s [%(asctime)s|%(module)s>%(funcName)s] %(message)s')
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger