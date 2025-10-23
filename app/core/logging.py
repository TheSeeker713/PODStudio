"""
Logging Configuration
Structured logging for file + console output

STEP 3: Placeholder logger factory documented for future JSON logging.
TODO (Step 4+): Implement JSON logs with rotation, file output, and log levels per environment.
"""

import logging


def get_logger(name: str, level: int | None = None) -> logging.Logger:
    """
    Get or create a logger with the given name

    Args:
        name: Logger name (usually __name__)
        level: Optional log level override

    Returns:
        Configured logger instance

    TODO (Step 4+): Add JSON formatting, file rotation, environment-based levels
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Only configure if not already configured
        logger.setLevel(level or logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Default logger for module-level usage
logger = get_logger("podstudio")
