import logging
import inspect

VERBOSE_LEVEL_NUM = 15
VERBOSE_LEVEL_NAME = "VERBOSE"

def _verbose(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE_LEVEL_NUM):
        kwargs.setdefault('stacklevel', 2)
        self._log(VERBOSE_LEVEL_NUM, message, args, **kwargs)

def setup_logging(log_level: str = "INFO"):
    """
    Configures the logging system with a custom VERBOSE level.
    """
    logging.addLevelName(VERBOSE_LEVEL_NUM, VERBOSE_LEVEL_NAME)
    logging.Logger.verbose = _verbose

    if isinstance(log_level, str):
        level_name = log_level.upper()
        if level_name == "VERBOSE":
            level = VERBOSE_LEVEL_NUM
        else:
            level = getattr(logging, level_name, logging.INFO)
    else:
        level = log_level

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def get_logger(name=None):
    return logging.getLogger(name)