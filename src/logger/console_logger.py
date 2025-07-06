"""logger.py"""

from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40


class ConsoleLogger:
    def __init__(self, level=LogLevel.INFO):
        if not isinstance(level, LogLevel):
            raise ValueError(f"Invalid log level: {level}")
        self.level = level

    def log(self, level: LogLevel, msg: str):
        if not isinstance(level, LogLevel):
            raise ValueError(f"Invalid log level: {level}")
        if level >= self.level:
            print(f"[{level.name}] {msg}")

    def debug(self, msg):
        self.log(LogLevel.DEBUG, msg)

    def info(self, msg):
        self.log(LogLevel.INFO, msg)

    def warn(self, msg):
        self.log(LogLevel.WARN, msg)

    def error(self, msg):
        self.log(LogLevel.ERROR, msg)
