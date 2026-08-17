"""Centralized Logging Setup for SPECTRA-XDR."""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configures structured application logging across SPECTRA-XDR modules.
    
    Log format includes timestamp, log level, module name, line number, and message.
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level.upper(),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Reduce log noise from third-party libraries if needed
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Retrieves a logger instance for a given module name."""
    return logging.getLogger(name)
