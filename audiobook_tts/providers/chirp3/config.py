from __future__ import annotations

import os
from dataclasses import dataclass

from audiobook_tts.config import load_environment


DEFAULT_VOICE = "ru-RU-Chirp3-HD-Kore"


@dataclass(frozen=True)
class Chirp3Settings:
    voice: str


def load_settings(*, voice_override: str | None = None) -> Chirp3Settings:
    load_environment()
    voice = (
        (voice_override or "").strip()
        or os.getenv("CHIRP3_VOICE", "").strip()
        or DEFAULT_VOICE
    )
    return Chirp3Settings(voice=voice)
