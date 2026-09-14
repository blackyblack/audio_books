from __future__ import annotations

import base64
import wave
from pathlib import Path
from typing import Any, Callable

from audiobook_tts.markup import Document
from audiobook_tts.providers.base import ProviderError
from audiobook_tts.providers.google.markup import compile_document


class GoogleProvider:
    SUPPORTED_MODELS = frozenset({"gemini-2.5-pro-preview-tts"})
    OUTPUT_SUFFIX = ".wav"
    SAMPLE_RATE = 24_000

    def __init__(
        self,
        *,
        api_key: str,
        voice: str,
        client_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._api_key = api_key
        self._voice = voice
        self._client_factory = client_factory

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path:
        if model not in self.SUPPORTED_MODELS:
            supported = ", ".join(sorted(self.SUPPORTED_MODELS))
            raise ProviderError(f"Unsupported model '{model}'. Supported: {supported}.")
        if output.suffix.lower() != self.OUTPUT_SUFFIX:
            raise ProviderError("Google Gemini TTS output must use the .wav extension.")

        client_factory = self._client_factory
        if client_factory is None:
            try:
                from google import genai
            except ImportError as exc:  # pragma: no cover - installation failure path
                raise ProviderError(
                    "The Google Gen AI SDK is not installed. "
                    "Run: python -m pip install -e ."
                ) from exc
            client_factory = genai.Client

        prompt = compile_document(document)
        output = output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_name(f"{output.name}.part")

        try:
            client = client_factory(api_key=self._api_key)
            interaction = client.interactions.create(
                model=model,
                input=prompt,
                response_format={"type": "audio"},
                generation_config={"speech_config": [{"voice": self._voice}]},
            )
            encoded_audio = interaction.output_audio.data
            pcm = base64.b64decode(encoded_audio, validate=True)
            self._write_wave(partial, pcm)
            partial.replace(output)
        except Exception as exc:
            partial.unlink(missing_ok=True)
            if isinstance(exc, ProviderError):
                raise
            raise ProviderError(f"Google generation failed: {exc}") from exc

        return output.resolve()

    @classmethod
    def _write_wave(cls, path: Path, pcm: bytes) -> None:
        if not pcm:
            raise ProviderError("Google returned an empty audio response.")
        with wave.open(str(path), "wb") as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(2)
            audio_file.setframerate(cls.SAMPLE_RATE)
            audio_file.writeframes(pcm)
