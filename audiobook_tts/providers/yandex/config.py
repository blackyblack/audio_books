from __future__ import annotations

import os
from dataclasses import dataclass

from audiobook_tts.config import ConfigurationError, load_environment


DEFAULT_VOICE = "marina"


@dataclass(frozen=True)
class YandexSettings:
    api_key: str
    voice: str


def load_settings(*, voice_override: str | None = None) -> YandexSettings:
    load_environment()
    api_key = os.getenv("YANDEX_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "Missing configuration: YANDEX_API_KEY. Add it to .env; "
            "see audiobook_tts/providers/yandex/README.md."
        )

    voice = (
        (voice_override or "").strip()
        or os.getenv("YANDEX_VOICE", "").strip()
        or DEFAULT_VOICE
    )
    return YandexSettings(api_key=api_key, voice=voice)
