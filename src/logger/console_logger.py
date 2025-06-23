"""logger.py"""


class ConsoleLogger:
    def __init__(self, level="INFO"):
        self.levels = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
        if level not in self.levels:
            raise ValueError(f"Invalid log level: {level}")
        self.level = level

    def log(self, level, msg):
        if level not in self.levels:
            raise ValueError(f"Invalid log level: {level}")
        if self.levels[level] >= self.levels[self.level]:
            print(f"[{level}] {msg}")

    def debug(self, msg):
        self.log("DEBUG", msg)

    def info(self, msg):
        self.log("INFO", msg)

    def warn(self, msg):
        self.log("WARN", msg)

    def error(self, msg):
        self.log("ERROR", msg)
