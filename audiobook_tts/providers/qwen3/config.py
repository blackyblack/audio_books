from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from audiobook_tts.config import ConfigurationError, load_environment


DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/api/v1"
DEFAULT_VOICE_PROMPT = (
    "A composed female Russian audiobook narrator in her mid-thirties, with a "
    "warm, clear, natural voice, precise articulation, restrained emotion, a "
    "measured pace, and a rich but not theatrical timbre."
)
DEFAULT_VOICE_CACHE = Path(".qwen3-tts-vd-voice")


@dataclass(frozen=True)
class Qwen3Settings:
    api_key: str
    voice: str | None
    base_url: str
    voice_prompt: str
    voice_cache: Path


def load_settings(*, voice_override: str | None = None) -> Qwen3Settings:
    load_environment()
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "Missing configuration: DASHSCOPE_API_KEY. Add it to .env; "
            "see audiobook_tts/providers/qwen3/README.md."
        )

    voice = (voice_override or "").strip() or os.getenv("QWEN_VOICE", "").strip()
    base_url = os.getenv("QWEN_BASE_URL", "").strip() or DEFAULT_BASE_URL
    voice_prompt = (
        os.getenv("QWEN_VOICE_PROMPT", "").strip() or DEFAULT_VOICE_PROMPT
    )
    cache_value = os.getenv("QWEN_VOICE_CACHE", "").strip()
    return Qwen3Settings(
        api_key=api_key,
        voice=voice or None,
        base_url=base_url.rstrip("/"),
        voice_prompt=voice_prompt,
        voice_cache=Path(cache_value) if cache_value else DEFAULT_VOICE_CACHE,
    )
