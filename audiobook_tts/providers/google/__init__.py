"""Google Gemini text-to-speech integration."""

from audiobook_tts.providers.google.config import load_settings
from audiobook_tts.providers.google.provider import GoogleProvider

__all__ = ["GoogleProvider", "load_settings"]
