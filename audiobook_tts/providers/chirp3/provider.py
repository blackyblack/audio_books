from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from audiobook_tts.markup import Document
from audiobook_tts.providers.base import ProviderError, warn_ignored_narrator_style
from audiobook_tts.providers.chirp3.markup import compile_document


class Chirp3Provider:
    MODEL = "chirp3-hd"
    SUPPORTED_MODELS = frozenset({MODEL})
    OUTPUT_SUFFIX = ".mp3"
    LANGUAGE_CODE = "ru-RU"

    def __init__(
        self,
        *,
        voice: str,
        client_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._voice = voice
        self._client_factory = client_factory

    @classmethod
    def output_suffix_for(cls, model: str) -> str:
        cls._validate_model(model)
        return cls.OUTPUT_SUFFIX

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path:
        self._validate_model(model)
        if output.suffix.lower() != self.OUTPUT_SUFFIX:
            raise ProviderError(f"{model} output must use the .mp3 extension.")
        warn_ignored_narrator_style(document, "Google Cloud Chirp 3 HD")

        client_factory = self._client_factory
        if client_factory is None:
            try:
                from google.cloud import texttospeech
            except ImportError as exc:  # pragma: no cover
                raise ProviderError(
                    "The Google Cloud Text-to-Speech SDK is not installed. "
                    "Run: python -m pip install -e ."
                ) from exc
            client_factory = texttospeech.TextToSpeechClient

        output = output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_name(f"{output.name}.part")
        request = {
            "input": {"ssml": compile_document(document)},
            "voice": {"language_code": self.LANGUAGE_CODE, "name": self._voice},
            "audio_config": {"audio_encoding": "MP3"},
        }

        try:
            response = client_factory().synthesize_speech(request=request)
            audio = response.audio_content
            if not audio:
                raise ProviderError("Chirp 3 returned an empty audio response.")
            partial.write_bytes(audio)
            partial.replace(output)
        except Exception as exc:
            partial.unlink(missing_ok=True)
            if isinstance(exc, ProviderError):
                raise
            raise ProviderError(f"Chirp 3 generation failed: {exc}") from exc

        return output.resolve()

    @classmethod
    def _validate_model(cls, model: str) -> None:
        if model not in cls.SUPPORTED_MODELS:
            supported = ", ".join(sorted(cls.SUPPORTED_MODELS))
            raise ProviderError(f"Unsupported model '{model}'. Supported: {supported}.")
