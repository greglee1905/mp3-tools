import logging

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up and return a logger with the specified name and level.

    :name: Name of the logger.
    :level: Logging level (default: logging.INFO).
    :returns: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger