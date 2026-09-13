from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Raised when required application configuration is missing."""


DEFAULT_ELEVENLABS_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George


@dataclass(frozen=True)
class Settings:
    elevenlabs_api_key: str
    elevenlabs_voice_id: str


def load_environment() -> None:
    """Load the local `.env` without overriding explicit process variables."""
    load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)


def load_settings(*, voice_id_override: str | None = None) -> Settings:
    """Read and validate the ElevenLabs settings."""

    load_environment()
    api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "Missing configuration: ELEVENLABS_API_KEY. Add it to .env; "
            "see Readme.md for setup instructions."
        )

    voice_id = (
        (voice_id_override or "").strip()
        or os.getenv("ELEVENLABS_VOICE_ID", "").strip()
        or DEFAULT_ELEVENLABS_VOICE_ID
    )

    return Settings(
        elevenlabs_api_key=api_key,
        elevenlabs_voice_id=voice_id,
    )
