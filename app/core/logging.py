"""
Structured logging configuration.
Supports both text and JSON output formats.
"""
import json
import logging
import logging.config
from datetime import datetime
from pathlib import Path

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data, default=str)


def setup_logging() -> None:
    """Configure application logging."""
    # Create logs directory if it doesn't exist
    if settings.LOG_FILE:
        Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "text": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": settings.LOG_FORMAT,
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
        },
    }

    # Add file handler if LOG_FILE is set
    if settings.LOG_FILE:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.LOG_FILE,
            "maxBytes": 10 * 1024 * 1024,  # 10MB
            "backupCount": 5,
            "formatter": settings.LOG_FORMAT,
        }
        config["root"]["handlers"].append("file")

    logging.config.dictConfig(config)
