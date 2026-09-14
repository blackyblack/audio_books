from __future__ import annotations

import base64
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace

from audiobook_tts.markup import parse
from audiobook_tts.providers import ProviderError
from audiobook_tts.providers.google import GoogleProvider


class GoogleProviderTests(unittest.TestCase):
    def test_calls_sdk_and_writes_wave(self) -> None:
        calls: dict[str, object] = {}
        pcm = b"\x01\x00\x02\x00"

        class FakeInteractions:
            def create(self, **kwargs: object):
                calls.update(kwargs)
                return SimpleNamespace(
                    output_audio=SimpleNamespace(
                        data=base64.b64encode(pcm).decode("ascii")
                    )
                )

        class FakeClient:
            def __init__(self, *, api_key: str) -> None:
                calls["api_key"] = api_key
                self.interactions = FakeInteractions()

        provider = GoogleProvider(
            api_key="secret", voice="Kore", client_factory=FakeClient
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "sample.wav")
            result = provider.synthesize(
                model="gemini-2.5-pro-preview-tts",
                document=parse("Пример."),
                output=output,
            )
            with wave.open(str(output), "rb") as audio_file:
                self.assertEqual(audio_file.getframerate(), 24_000)
                self.assertEqual(audio_file.readframes(2), pcm)
            self.assertEqual(result, output.resolve())

        self.assertEqual(calls["api_key"], "secret")
        self.assertEqual(calls["model"], "gemini-2.5-pro-preview-tts")
        self.assertEqual(calls["response_format"], {"type": "audio"})
        self.assertEqual(
            calls["generation_config"], {"speech_config": [{"voice": "Kore"}]}
        )
        self.assertIn("TRANSCRIPT:\nПример.", calls["input"])

    def test_requires_wave_output(self) -> None:
        provider = GoogleProvider(
            api_key="secret", voice="Kore", client_factory=lambda **_: None
        )
        with self.assertRaisesRegex(ProviderError, r"\.wav"):
            provider.synthesize(
                model="gemini-2.5-pro-preview-tts",
                document=parse("Пример."),
                output=Path("sample.mp3"),
            )


if __name__ == "__main__":
    unittest.main()
