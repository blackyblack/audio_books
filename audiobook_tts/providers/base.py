from pathlib import Path
from typing import Protocol

from audiobook_tts.markup import Document


class ProviderError(RuntimeError):
    """Raised when a speech provider cannot generate or save audio."""


class SpeechProvider(Protocol):
    OUTPUT_SUFFIX: str

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path: ...
