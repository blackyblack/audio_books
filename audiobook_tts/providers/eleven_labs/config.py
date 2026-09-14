from __future__ import annotations

import os
from dataclasses import dataclass

from audiobook_tts.config import ConfigurationError, load_environment


DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # George


@dataclass(frozen=True)
class ElevenLabsSettings:
    api_key: str
    voice_id: str


def load_settings(*, voice_id_override: str | None = None) -> ElevenLabsSettings:
    """Load and validate ElevenLabs settings after reading the local `.env`."""

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
        or DEFAULT_VOICE_ID
    )
    return ElevenLabsSettings(api_key=api_key, voice_id=voice_id)
