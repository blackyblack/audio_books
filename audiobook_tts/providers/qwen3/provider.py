from __future__ import annotations

import io
import wave
from pathlib import Path
from typing import Any, Callable

from audiobook_tts.markup import Document
from audiobook_tts.providers.base import ProviderError
from audiobook_tts.providers.qwen3.markup import compile_document


class Qwen3Provider:
    MODEL = "qwen3-tts-vd-2026-01-26"
    SUPPORTED_MODELS = frozenset({MODEL})
    OUTPUT_SUFFIX = ".wav"
    MAX_CHARACTERS = 600
    API_PATH = "/services/aigc/multimodal-generation/generation"
    VOICE_API_PATH = "/services/audio/tts/customization"
    VOICE_CREATION_MODEL = "qwen-voice-design"
    PREVIEW_TEXT = (
        "Вечерний свет медленно угасал, и над рекой поднимался прохладный туман."
    )

    def __init__(
        self,
        *,
        api_key: str,
        voice: str | None,
        base_url: str,
        voice_prompt: str,
        voice_cache: Path,
        session_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._api_key = api_key
        self._voice = voice
        self._base_url = base_url.rstrip("/")
        self._voice_prompt = voice_prompt
        self._voice_cache = voice_cache
        self._session_factory = session_factory

    @classmethod
    def output_suffix_for(cls, model: str) -> str:
        cls._validate_model(model)
        return cls.OUTPUT_SUFFIX

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path:
        self._validate_model(model)
        if output.suffix.lower() != self.OUTPUT_SUFFIX:
            raise ProviderError(f"{model} output must use the .wav extension.")

        session_factory = self._session_factory
        if session_factory is None:
            try:
                import requests
            except ImportError as exc:  # pragma: no cover
                raise ProviderError(
                    "The Requests package is not installed. "
                    "Run: python -m pip install -e ."
                ) from exc
            session_factory = requests.Session

        text = compile_document(document)
        chunks = self._split_text(text)
        output = output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_name(f"{output.name}.part")

        try:
            audio_parts = []
            with session_factory() as session:
                voice = self._resolve_voice(session)
                for chunk in chunks:
                    audio_parts.append(
                        self._generate_chunk(
                            session=session,
                            model=model,
                            text=chunk,
                            voice=voice,
                        )
                    )
            self._write_wav_parts(partial, audio_parts)
            partial.replace(output)
        except Exception as exc:
            partial.unlink(missing_ok=True)
            if isinstance(exc, ProviderError):
                raise
            raise ProviderError(f"Qwen3 generation failed: {exc}") from exc

        return output.resolve()

    def _generate_chunk(
        self, *, session: Any, model: str, text: str, voice: str
    ) -> bytes:
        response = session.post(
            f"{self._base_url}{self.API_PATH}",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": model,
                "input": {
                    "text": text,
                    "voice": voice,
                },
            },
            timeout=300,
        )
        response.raise_for_status()
        try:
            body = response.json()
            audio_url = body["output"]["audio"]["url"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderError("Qwen3 returned a malformed synthesis response.") from exc
        if not audio_url:
            raise ProviderError("Qwen3 returned no audio URL.")

        audio_response = session.get(audio_url, timeout=300)
        audio_response.raise_for_status()
        if not audio_response.content:
            raise ProviderError("Qwen3 returned an empty audio response.")
        return audio_response.content

    def _resolve_voice(self, session: Any) -> str:
        if self._voice:
            return self._voice

        cache = self._voice_cache.expanduser()
        try:
            if cache.is_file():
                cached_voice = cache.read_text(encoding="utf-8").strip()
                if cached_voice:
                    self._voice = cached_voice
                    return cached_voice
        except OSError as exc:
            raise ProviderError(f"Could not read Qwen3 voice cache '{cache}': {exc}") from exc

        voice = self._create_voice(session)
        partial = cache.with_name(f"{cache.name}.part")
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            partial.write_text(f"{voice}\n", encoding="utf-8")
            partial.replace(cache)
        except OSError as exc:
            partial.unlink(missing_ok=True)
            raise ProviderError(f"Could not save Qwen3 voice cache '{cache}': {exc}") from exc
        self._voice = voice
        return voice

    def _create_voice(self, session: Any) -> str:
        response = session.post(
            f"{self._base_url}{self.VOICE_API_PATH}",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self.VOICE_CREATION_MODEL,
                "input": {
                    "action": "create",
                    "target_model": self.MODEL,
                    "preferred_name": "audiobook_ru",
                    "voice_prompt": self._voice_prompt,
                    "preview_text": self.PREVIEW_TEXT,
                },
                "parameters": {
                    "sample_rate": 24_000,
                    "response_format": "wav",
                },
            },
            timeout=300,
        )
        response.raise_for_status()
        try:
            voice = response.json()["output"]["voice"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderError("Qwen3 returned a malformed voice-design response.") from exc
        if not voice:
            raise ProviderError("Qwen3 returned no designed voice ID.")
        return voice

    @classmethod
    def _split_text(cls, text: str) -> list[str]:
        remaining = text.strip()
        chunks: list[str] = []
        boundaries = ("\n\n", ". ", "! ", "? ", "… ", "; ", ", ", " ")
        while len(remaining) > cls.MAX_CHARACTERS:
            window = remaining[: cls.MAX_CHARACTERS + 1]
            cuts = [
                index + len(boundary)
                for boundary in boundaries
                if (index := window.rfind(boundary)) >= 0
            ]
            cut = max(cuts, default=cls.MAX_CHARACTERS)
            chunks.append(remaining[:cut].strip())
            remaining = remaining[cut:].strip()
        if remaining:
            chunks.append(remaining)
        if not chunks:
            raise ProviderError("Qwen3 input must not be empty.")
        return chunks

    @staticmethod
    def _write_wav_parts(path: Path, audio_parts: list[bytes]) -> None:
        expected_params = None
        frames = []
        try:
            for audio in audio_parts:
                with wave.open(io.BytesIO(audio), "rb") as source:
                    params = (
                        source.getnchannels(),
                        source.getsampwidth(),
                        source.getframerate(),
                        source.getcomptype(),
                    )
                    if expected_params is None:
                        expected_params = params
                    elif params != expected_params:
                        raise ProviderError(
                            "Qwen3 returned incompatible audio formats across chunks."
                        )
                    frames.append(source.readframes(source.getnframes()))
        except (EOFError, wave.Error) as exc:
            raise ProviderError("Qwen3 returned malformed WAV audio.") from exc

        if expected_params is None:
            raise ProviderError("Qwen3 returned an empty audio response.")
        channels, sample_width, frame_rate, compression = expected_params
        if compression != "NONE":
            raise ProviderError("Qwen3 returned compressed WAV audio.")
        with wave.open(str(path), "wb") as target:
            target.setnchannels(channels)
            target.setsampwidth(sample_width)
            target.setframerate(frame_rate)
            for frame_block in frames:
                target.writeframes(frame_block)

    @classmethod
    def _validate_model(cls, model: str) -> None:
        if model not in cls.SUPPORTED_MODELS:
            supported = ", ".join(sorted(cls.SUPPORTED_MODELS))
            raise ProviderError(f"Unsupported model '{model}'. Supported: {supported}.")
