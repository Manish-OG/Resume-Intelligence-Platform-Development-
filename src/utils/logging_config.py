"""
Centralized logging configuration for the Resume Intelligence Platform.

This module configures the application's logging system. It should be
initialized once during application startup before any modules begin logging.
"""

import logging


def configure_logging() -> None:
    """
    Configure the application's logging system.

    This function initializes the root logger with:
    - INFO as the default log level
    - A consistent log format
    - Console output

    It should be called exactly once during application startup.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )