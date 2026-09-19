import sys
from pathlib import Path
from typing import Protocol

from audiobook_tts.markup import Document


class ProviderError(RuntimeError):
    """Raised when a speech provider cannot generate or save audio."""


def warn_ignored_narrator_style(document: Document, provider: str) -> None:
    """Warn when a provider ignores the optional ABM narrator style."""

    if document.narrator_style is not None:
        print(
            f"warning: {provider} ignores the ABM narrator style.",
            file=sys.stderr,
        )


class SpeechProvider(Protocol):
    def output_suffix_for(self, model: str) -> str: ...

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path: ...
