from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Raised when required application configuration is missing."""


def load_environment() -> None:
    """Load the local `.env` without overriding explicit process variables."""
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
