from __future__ import annotations

import base64
import binascii
import json
from pathlib import Path
from typing import Any, Callable

from audiobook_tts.markup import Document
from audiobook_tts.providers.base import ProviderError
from audiobook_tts.providers.yandex.markup import compile_document


class YandexProvider:
    SUPPORTED_MODELS = frozenset({"yandex-speechkit-v3"})
    OUTPUT_SUFFIX = ".mp3"
    API_URL = "https://tts.api.cloud.yandex.net/tts/v3/utteranceSynthesis"

    def __init__(
        self,
        *,
        api_key: str,
        voice: str,
        session_factory: Callable[[], Any] | None = None,
    ) -> None:
        self._api_key = api_key
        self._voice = voice
        self._session_factory = session_factory

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path:
        if model not in self.SUPPORTED_MODELS:
            supported = ", ".join(sorted(self.SUPPORTED_MODELS))
            raise ProviderError(f"Unsupported model '{model}'. Supported: {supported}.")

        session_factory = self._session_factory
        if session_factory is None:
            try:
                import requests
            except ImportError as exc:  # pragma: no cover - installation failure path
                raise ProviderError(
                    "The Requests package is not installed. "
                    "Run: python -m pip install -e ."
                ) from exc
            session_factory = requests.Session

        output = output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_name(f"{output.name}.part")
        payload = {
            "text": compile_document(document),
            "hints": [{"voice": self._voice}],
            "outputAudioSpec": {
                "containerAudio": {"containerAudioType": "MP3"}
            },
            "loudnessNormalizationType": "LUFS",
            "unsafeMode": True,
        }

        try:
            with session_factory() as session:
                response = session.post(
                    self.API_URL,
                    headers={"Authorization": f"Api-Key {self._api_key}"},
                    json=payload,
                    stream=True,
                    timeout=300,
                )
                response.raise_for_status()
                self._write_audio_chunks(partial, response.iter_lines())
            partial.replace(output)
        except Exception as exc:
            partial.unlink(missing_ok=True)
            if isinstance(exc, ProviderError):
                raise
            raise ProviderError(f"Yandex generation failed: {exc}") from exc

        return output.resolve()

    @staticmethod
    def _write_audio_chunks(path: Path, lines: Any) -> None:
        wrote_audio = False
        with path.open("wb") as audio_file:
            for line in lines:
                if not line:
                    continue
                try:
                    response_part = json.loads(line)
                    encoded = (
                        response_part.get("result", {})
                        .get("audioChunk", {})
                        .get("data")
                    )
                    if encoded:
                        audio_file.write(base64.b64decode(encoded, validate=True))
                        wrote_audio = True
                except (json.JSONDecodeError, TypeError, ValueError, binascii.Error) as exc:
                    raise ProviderError(
                        "Yandex returned a malformed audio response."
                    ) from exc

        if not wrote_audio:
            raise ProviderError("Yandex returned an empty audio response.")
