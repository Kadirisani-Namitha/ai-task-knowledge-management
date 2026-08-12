import logging
import sys

from app.core.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Avoid adding duplicate handlers on reload (uvicorn --reload)
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("passlib").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
