import pytest
from logger.console_logger import ConsoleLogger, LogLevel


def test_logger_default_level():
    logger = ConsoleLogger()
    assert logger.level == LogLevel.INFO


def test_logger_custom_level():
    logger = ConsoleLogger(LogLevel.DEBUG)
    assert logger.level == LogLevel.DEBUG


def test_invalid_level():
    with pytest.raises(ValueError, match="Invalid log level"):
        ConsoleLogger(level=123)


def test_log_levels(capsys):
    logger = ConsoleLogger(LogLevel.DEBUG)

    logger.debug("debug message")
    logger.info("info message")
    logger.warn("warn message")
    logger.error("error message")

    captured = capsys.readouterr()
    output_lines = captured.out.strip().split("\n")

    assert output_lines[0] == "[DEBUG] debug message"
    assert output_lines[1] == "[INFO] info message"
    assert output_lines[2] == "[WARN] warn message"
    assert output_lines[3] == "[ERROR] error message"


def test_level_filtering(capsys):
    logger = ConsoleLogger(LogLevel.WARN)

    logger.debug("debug message")  # Should not print
    logger.info("info message")  # Should not print
    logger.warn("warn message")  # Should print
    logger.error("error message")  # Should print

    captured = capsys.readouterr()
    output_lines = captured.out.strip().split("\n")

    assert len(output_lines) == 2
    assert output_lines[0] == "[WARN] warn message"
    assert output_lines[1] == "[ERROR] error message"


def test_invalid_log_call():
    logger = ConsoleLogger()
    with pytest.raises(ValueError, match="Invalid log level"):
        logger.log(999, "invalid level message")
