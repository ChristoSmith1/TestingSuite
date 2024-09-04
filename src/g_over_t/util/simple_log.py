"""
A simple console logger with reasonable defaults.

Will use the `rich` module for pretty-printed Console messaging, if the module is available.

Usage:

>>> from simple_log import logger
>>> logger.info("This is an informational level message")
21:40:55 INFO     This is an informational level message
"""

import logging
try:
    import rich.logging
    # import fake
    _rich_available = True
except ImportError:
    _rich_available = False


if _rich_available:
    _console_format = "%(message)s"
    _console_handler = rich.logging.RichHandler(
        omit_repeated_times=False,
        rich_tracebacks=True,
        level=logging.DEBUG,
    )
else:
    _console_format = "%(asctime)s [%(levelname)-8s] %(message)s"
    _console_handler = logging.StreamHandler()
    _console_handler.setLevel(logging.DEBUG)

_console_format
_console_handler.setFormatter(logging.Formatter(
    fmt=_console_format,
    datefmt="%X"
))


logger = logging.getLogger("simple_log")
"""The default logger instance that users should use.

>>> from simple_log import logger
>>> logger.info("This is an informational level message")
21:40:55 INFO     This is an informational level message
"""
if not logger.handlers:
    logger.addHandler(_console_handler)

def set_level(level: int | str) -> None:
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


set_level(logging.DEBUG)


def set_root(logger: logging.Logger = logger) -> None:
    """Override the root logger of the Python `logging` module.
    
    Generally, this works fine, but it can cause weird issues. I don't usually 
    recommend doing this."""
    logging.root = logger


# Convenience function exports, so that `simple_log.info()` works as expected
log = logger.log
critical = logger.critical
exception = logger.exception
error = logger.error
warning = logger.warning
info = logger.info
debug = logger.debug