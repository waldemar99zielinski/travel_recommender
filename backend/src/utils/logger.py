import logging

from utils.singleton import SingletonMeta

GREY = "\x1b[38;20m"
CYAN = "\x1b[36;20m"
GREEN = "\x1b[32;20m"
YELLOW = "\x1b[33;20m"
RED = "\x1b[31;20m"
BOLD_RED = "\x1b[31;1m"
RESET = "\x1b[0m"

VERBOSE_LEVEL_NUM = 15
VERBOSE_LEVEL_NAME = "VERBOSE"

class CustomFormatter(logging.Formatter):
    fmt = "%(asctime)s - [%(name)s %(funcName)s:%(lineno)d] - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + fmt + RESET,
        VERBOSE_LEVEL_NUM: CYAN + fmt + RESET,
        logging.INFO: GREEN + fmt + RESET,
        logging.WARNING: YELLOW + fmt + RESET,
        logging.ERROR: RED + fmt + RESET,
        logging.CRITICAL: BOLD_RED + fmt + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.fmt)
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def _verbose_method(self, message, *args, **kwargs):
    if self.isEnabledFor(VERBOSE_LEVEL_NUM):
        kwargs.setdefault('stacklevel', 2)
        self._log(VERBOSE_LEVEL_NUM, message, args, **kwargs)


class LoggerManager(metaclass=SingletonMeta):
    _loggers: dict[str, logging.Logger] = {}
    _log_level: int | str = logging.DEBUG

    def __init__(self, log_level: int | str = VERBOSE_LEVEL_NUM):
        self._log_level = log_level
        LoggerManager._log_level = log_level

        if not hasattr(logging.Logger, "verbose"):
            logging.addLevelName(VERBOSE_LEVEL_NUM, VERBOSE_LEVEL_NAME)
            setattr(logging.Logger, "verbose", _verbose_method)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        cls()
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(cls._log_level)

            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(CustomFormatter())
                logger.addHandler(handler)
            logger.propagate = False
            cls._loggers[name] = logger

        return cls._loggers[name]
