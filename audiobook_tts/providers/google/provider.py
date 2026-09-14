from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Callable

from audiobook_tts.markup import Document
from audiobook_tts.providers.base import ProviderError
from audiobook_tts.providers.google.markup import compile_document


class GoogleProvider:
    SUPPORTED_MODELS = frozenset({"gemini-2.5-pro-preview-tts"})
    OUTPUT_SUFFIX = ".mp3"
    OUTPUT_MIME_TYPE = "audio/mp3"

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
            raise ProviderError("Google Gemini TTS output must use the .mp3 extension.")

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
                response_format={
                    "type": "audio",
                    "mime_type": self.OUTPUT_MIME_TYPE,
                    "delivery": "inline",
                },
                generation_config={"speech_config": [{"voice": self._voice}]},
            )
            audio = interaction.output_audio
            mime_type = getattr(audio, "mime_type", None)
            if mime_type and mime_type not in {self.OUTPUT_MIME_TYPE, "audio/mpeg"}:
                raise ProviderError(
                    f"Google returned '{mime_type}' after MP3 was requested."
                )
            encoded_audio = audio.data
            audio_bytes = base64.b64decode(encoded_audio, validate=True)
            self._write_audio(partial, audio_bytes)
            partial.replace(output)
        except Exception as exc:
            partial.unlink(missing_ok=True)
            if isinstance(exc, ProviderError):
                raise
            raise ProviderError(f"Google generation failed: {exc}") from exc

        return output.resolve()

    @staticmethod
    def _write_audio(path: Path, audio: bytes) -> None:
        if not audio:
            raise ProviderError("Google returned an empty audio response.")
        path.write_bytes(audio)
