#!/usr/bin/env python3
"""mokaguys_logger.py

Log messages using the python standard library logging module.

Version: 1.0
Timestamp: 30/05/19
"""

import logging
from logging.config import dictConfig


def log_setup(logfile_path, syslog="/dev/log"):
    """Setup application logging using python's standard library logging module

    Args:
        logfile_name(str): The name of the output logfile written to by the file handler
        syslog(str): Output target for the system log handler
    """
    logging_config = dict(
        version=1.0,
        formatters={
            "log_formatter": {
                "format": "{asctime} {name}.{module}: {levelname} - {message}",
                "style": "{",
                "datefmt": r"%Y-%m-%d %H:%M:%S",
            }
        },
        handlers={
            # DEBUG message are ommitted from the console output by setting the stream handler level
            # to INFO, making console outputs easier to read. DEBUG messages are still written to
            # the application logfile and system log.
            "stream_handler": {
                "class": "logging.StreamHandler",
                "formatter": "log_formatter",
                "level": logging.INFO,
            },
            "file_handler": {
                "class": "logging.FileHandler",
                "formatter": "log_formatter",
                "level": logging.DEBUG,
                "filename": logfile_path,
            },
            "syslog_handler": {
                "class": "logging.handlers.SysLogHandler",
                "formatter": "log_formatter",
                "level": logging.DEBUG,
                "address": syslog,
            },
        },
        root={
            "handlers": ["file_handler", "stream_handler", "syslog_handler"],
            "level": logging.DEBUG,
        },
    )
    dictConfig(logging_config)


if __name__ == "__main__":
    log_setup()
    log = logging.getLogger("TEST")
    log.info("TEST")
