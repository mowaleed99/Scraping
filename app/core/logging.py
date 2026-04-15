from __future__ import annotations

import logging
import sys

import structlog

from app.core.config import get_settings


def setup_logging() -> None:
    """
    Configure structlog for structured JSON logging in production
    and pretty console logging in development.
    Called once at application startup.
    """
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Standard library logging baseline
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        # JSON output for Modal log sinks / external aggregators
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Pretty coloured output for local development
        structlog.configure(
            processors=[
                *shared_processors,
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Return a bound structlog logger.  Use as module-level constant:

        log = get_logger(__name__)
    """
    return structlog.get_logger(name)
