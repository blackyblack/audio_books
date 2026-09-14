from __future__ import annotations

import os
from dataclasses import dataclass

from audiobook_tts.config import ConfigurationError, load_environment


DEFAULT_VOICE = "Kore"


@dataclass(frozen=True)
class GoogleSettings:
    api_key: str
    voice: str


def load_settings(*, voice_override: str | None = None) -> GoogleSettings:
    load_environment()
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "Missing configuration: GOOGLE_API_KEY. Add it to .env; "
            "see audiobook_tts/providers/google/README.md."
        )

    voice = (
        (voice_override or "").strip()
        or os.getenv("GOOGLE_VOICE", "").strip()
        or DEFAULT_VOICE
    )
    return GoogleSettings(api_key=api_key, voice=voice)
