import logging
import sys


def setup_logging(log_level_str: str) -> None:
    """
    Configure the logging settings for the application.

    This function sets up logging to output log messages to the standard output stream
    in a structured JSON format. The log level is determined by the provided string,
    defaulting to INFO if the string does not match a valid log level.

    Args:
        log_level_str (str): The desired log level as a string (e.g., 'DEBUG', 'INFO', 'WARNING').

    Returns:
        None
    """
    log_level: int = getattr(logging, log_level_str, logging.INFO)
    logging.basicConfig(
        stream=sys.stdout,
        level=log_level,
        format='{"timestamp": "%(asctime)s.%(msecs)03dZ", "level": "%(levelname)s", "message": "%(message)s"}',
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    logging.log(logging.INFO, "Log level set to %s", log_level_str)
