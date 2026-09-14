from __future__ import annotations

import base64
import wave
from pathlib import Path
from typing import Any, Callable

from audiobook_tts.markup import Document
from audiobook_tts.providers.base import ProviderError
from audiobook_tts.providers.google.markup import compile_document


class GoogleProvider:
    FLASH_MODEL = "gemini-2.5-flash-preview-tts"
    PRO_MODEL = "gemini-2.5-pro-preview-tts"
    FLASH_31_MODEL = "gemini-3.1-flash-tts-preview"
    MODEL_OUTPUTS = {
        FLASH_MODEL: (".wav", "audio/l16"),
        PRO_MODEL: (".wav", "audio/l16"),
        FLASH_31_MODEL: (".wav", "audio/l16"),
    }
    SUPPORTED_MODELS = frozenset(MODEL_OUTPUTS)
    OUTPUT_SAMPLE_RATE = 24_000
    OUTPUT_CHANNELS = 1
    OUTPUT_SAMPLE_WIDTH = 2

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
        output_suffix, output_mime_type = self._output_format(model)
        if output.suffix.lower() != output_suffix:
            raise ProviderError(
                f"{model} output must use the {output_suffix} extension."
            )

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
            response_format: dict[str, str] = {"type": "audio"}

            interaction = client.interactions.create(
                model=model,
                input=prompt,
                response_format=response_format,
                generation_config={"speech_config": [{"voice": self._voice}]},
            )
            audio = interaction.output_audio
            mime_type = getattr(audio, "mime_type", None)
            response_mime_type = (
                mime_type.partition(";")[0].strip().lower() if mime_type else None
            )
            accepted_mime_types = {output_mime_type}
            if response_mime_type and response_mime_type not in accepted_mime_types:
                raise ProviderError(
                    f"Google returned '{mime_type}'; expected the default PCM format."
                )
            encoded_audio = audio.data
            audio_bytes = base64.b64decode(encoded_audio, validate=True)
            if output_mime_type == "audio/l16":
                self._write_wav(partial, audio_bytes)
            else:
                self._write_audio(partial, audio_bytes)
            partial.replace(output)
        except Exception as exc:
            partial.unlink(missing_ok=True)
            if isinstance(exc, ProviderError):
                raise
            raise ProviderError(f"Google generation failed: {exc}") from exc

        return output.resolve()

    @classmethod
    def output_suffix_for(cls, model: str) -> str:
        return cls._output_format(model)[0]

    @classmethod
    def _output_format(cls, model: str) -> tuple[str, str]:
        try:
            return cls.MODEL_OUTPUTS[model]
        except KeyError as exc:
            supported = ", ".join(sorted(cls.SUPPORTED_MODELS))
            raise ProviderError(
                f"Unsupported model '{model}'. Supported: {supported}."
            ) from exc

    @staticmethod
    def _write_audio(path: Path, audio: bytes) -> None:
        if not audio:
            raise ProviderError("Google returned an empty audio response.")
        path.write_bytes(audio)

    @classmethod
    def _write_wav(cls, path: Path, audio: bytes) -> None:
        if not audio:
            raise ProviderError("Google returned an empty audio response.")
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(cls.OUTPUT_CHANNELS)
            wav_file.setsampwidth(cls.OUTPUT_SAMPLE_WIDTH)
            wav_file.setframerate(cls.OUTPUT_SAMPLE_RATE)
            wav_file.writeframes(audio)
