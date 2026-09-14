"""Google Cloud Chirp 3 HD provider."""

from audiobook_tts.providers.chirp3.config import load_settings
from audiobook_tts.providers.chirp3.provider import Chirp3Provider

__all__ = ["Chirp3Provider", "load_settings"]
