"""Logging helpers for Power Pit."""
from __future__ import annotations

import logging


def configure_logging(verbose: bool = False) -> None:
    """Configure root logging handlers."""

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(message)s",
    )
