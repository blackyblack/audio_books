"""Yandex SpeechKit text-to-speech integration."""

from audiobook_tts.providers.yandex.config import load_settings
from audiobook_tts.providers.yandex.provider import YandexProvider

__all__ = ["YandexProvider", "load_settings"]
