"""ElevenLabs text-to-speech integration."""

from audiobook_tts.providers.eleven_labs.config import load_settings
from audiobook_tts.providers.eleven_labs.provider import ElevenLabsProvider

__all__ = ["ElevenLabsProvider", "load_settings"]
