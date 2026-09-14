from __future__ import annotations

import base64
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from audiobook_tts.markup import parse
from audiobook_tts.providers import ProviderError
from audiobook_tts.providers.google import GoogleProvider


class GoogleProviderTests(unittest.TestCase):
    def test_supports_flash_and_pro_models(self) -> None:
        self.assertEqual(
            GoogleProvider.SUPPORTED_MODELS,
            {
                "gemini-2.5-flash-preview-tts",
                "gemini-2.5-pro-preview-tts",
            },
        )

    def test_requests_and_writes_mp3(self) -> None:
        calls: dict[str, object] = {}
        mp3 = b"ID3audio"

        class FakeInteractions:
            def create(self, **kwargs: object):
                calls.update(kwargs)
                return SimpleNamespace(
                    output_audio=SimpleNamespace(
                        data=base64.b64encode(mp3).decode("ascii"),
                        mime_type="audio/mp3",
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
            output = Path(directory, "sample.mp3")
            result = provider.synthesize(
                model="gemini-2.5-flash-preview-tts",
                document=parse("Пример."),
                output=output,
            )
            self.assertEqual(output.read_bytes(), mp3)
            self.assertEqual(result, output.resolve())

        self.assertEqual(calls["api_key"], "secret")
        self.assertEqual(calls["model"], "gemini-2.5-flash-preview-tts")
        self.assertEqual(
            calls["response_format"],
            {
                "type": "audio",
                "mime_type": "audio/mp3",
            },
        )
        self.assertEqual(
            calls["generation_config"], {"speech_config": [{"voice": "Kore"}]}
        )
        self.assertIn("TRANSCRIPT:\nПример.", calls["input"])

    def test_requires_mp3_output(self) -> None:
        provider = GoogleProvider(
            api_key="secret", voice="Kore", client_factory=lambda **_: None
        )
        with self.assertRaisesRegex(ProviderError, r"\.mp3"):
            provider.synthesize(
                model="gemini-2.5-pro-preview-tts",
                document=parse("Пример."),
                output=Path("sample.wav"),
            )

    def test_rejects_an_unexpected_audio_format(self) -> None:
        class FakeInteractions:
            def create(self, **kwargs: object):
                return SimpleNamespace(
                    output_audio=SimpleNamespace(
                        data=base64.b64encode(b"wave").decode("ascii"),
                        mime_type="audio/wav",
                    )
                )

        class FakeClient:
            def __init__(self, *, api_key: str) -> None:
                self.interactions = FakeInteractions()

        provider = GoogleProvider(
            api_key="secret", voice="Kore", client_factory=FakeClient
        )
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(
            ProviderError, "after MP3 was requested"
        ):
            provider.synthesize(
                model="gemini-2.5-pro-preview-tts",
                document=parse("Пример."),
                output=Path(directory, "sample.mp3"),
            )


if __name__ == "__main__":
    unittest.main()
