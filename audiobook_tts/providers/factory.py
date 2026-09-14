from __future__ import annotations

from audiobook_tts.providers.base import ProviderError, SpeechProvider
from audiobook_tts.providers.chirp3 import Chirp3Provider
from audiobook_tts.providers.eleven_labs import ElevenLabsProvider
from audiobook_tts.providers.google import GoogleProvider
from audiobook_tts.providers.qwen3 import Qwen3Provider
from audiobook_tts.providers.yandex import YandexProvider


SUPPORTED_MODELS = frozenset(
    ElevenLabsProvider.SUPPORTED_MODELS
    | Chirp3Provider.SUPPORTED_MODELS
    | GoogleProvider.SUPPORTED_MODELS
    | Qwen3Provider.SUPPORTED_MODELS
    | YandexProvider.SUPPORTED_MODELS
)


def create_provider(
    *, model: str, voice_id_override: str | None = None
) -> SpeechProvider:
    if model in ElevenLabsProvider.SUPPORTED_MODELS:
        from audiobook_tts.providers.eleven_labs import load_settings

        settings = load_settings(voice_id_override=voice_id_override)
        return ElevenLabsProvider(api_key=settings.api_key, voice_id=settings.voice_id)

    if model in Chirp3Provider.SUPPORTED_MODELS:
        from audiobook_tts.providers.chirp3 import load_settings

        settings = load_settings(voice_override=voice_id_override)
        return Chirp3Provider(voice=settings.voice)

    if model in GoogleProvider.SUPPORTED_MODELS:
        from audiobook_tts.providers.google import load_settings

        settings = load_settings(voice_override=voice_id_override)
        return GoogleProvider(api_key=settings.api_key, voice=settings.voice)

    if model in Qwen3Provider.SUPPORTED_MODELS:
        from audiobook_tts.providers.qwen3 import load_settings

        settings = load_settings(voice_override=voice_id_override)
        return Qwen3Provider(
            api_key=settings.api_key,
            voice=settings.voice,
            base_url=settings.base_url,
            voice_prompt=settings.voice_prompt,
            voice_cache=settings.voice_cache,
        )

    if model in YandexProvider.SUPPORTED_MODELS:
        from audiobook_tts.providers.yandex import load_settings

        settings = load_settings(voice_override=voice_id_override)
        return YandexProvider(api_key=settings.api_key, voice=settings.voice)

    supported = ", ".join(sorted(SUPPORTED_MODELS))
    raise ProviderError(f"Unsupported model '{model}'. Supported: {supported}.")
