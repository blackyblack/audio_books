from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any, Callable

from audiobook_tts.markup import Document
from audiobook_tts.providers.base import ProviderError
from audiobook_tts.providers.eleven_labs.markup import compile_document


class ElevenLabsProvider:
    SUPPORTED_MODELS = frozenset({"eleven_v3"})
    OUTPUT_SUFFIX = ".mp3"
    MAX_CHARACTERS = 5_000
    OUTPUT_FORMAT = "mp3_44100_128"

    def __init__(
        self,
        *,
        api_key: str,
        voice_id: str,
        client_factory: Callable[..., Any] | None = None,
    ) -> None:
        self._api_key = api_key
        self._voice_id = voice_id
        self._client_factory = client_factory

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path:
        if model not in self.SUPPORTED_MODELS:
            supported = ", ".join(sorted(self.SUPPORTED_MODELS))
            raise ProviderError(f"Unsupported model '{model}'. Supported: {supported}.")
        text = compile_document(document)
        if len(text) > self.MAX_CHARACTERS:
            raise ProviderError(
                f"Compiled input is {len(text):,} characters; {model} accepts at most "
                f"{self.MAX_CHARACTERS:,} per request."
            )

        client_factory = self._client_factory
        if client_factory is None:
            try:
                from elevenlabs.client import ElevenLabs
            except ImportError as exc:  # pragma: no cover - installation failure path
                raise ProviderError(
                    "The ElevenLabs SDK is not installed. "
                    "Run: python -m pip install -e ."
                ) from exc
            client_factory = ElevenLabs

        output = output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_name(f"{output.name}.part")

        try:
            client = client_factory(api_key=self._api_key)
            audio = client.text_to_speech.convert(
                voice_id=self._voice_id,
                text=text,
                model_id=model,
                output_format=self.OUTPUT_FORMAT,
            )
            self._write_audio(partial, audio)
            partial.replace(output)
        except Exception as exc:
            partial.unlink(missing_ok=True)
            if isinstance(exc, ProviderError):
                raise
            raise ProviderError(f"ElevenLabs generation failed: {exc}") from exc

        return output.resolve()

    @staticmethod
    def _write_audio(path: Path, audio: bytes | Iterable[bytes]) -> None:
        with path.open("wb") as audio_file:
            if isinstance(audio, bytes):
                audio_file.write(audio)
            else:
                for chunk in audio:
                    if chunk:
                        audio_file.write(chunk)

        if path.stat().st_size == 0:
            raise ProviderError("ElevenLabs returned an empty audio response.")
