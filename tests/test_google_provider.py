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
    def test_supports_flash_and_pro_models(self) -> None:
        self.assertEqual(
            GoogleProvider.SUPPORTED_MODELS,
            {
                "gemini-2.5-flash-preview-tts",
                "gemini-2.5-pro-preview-tts",
            },
        )
        self.assertEqual(
            GoogleProvider.output_suffix_for("gemini-2.5-flash-preview-tts"),
            ".wav",
        )
        self.assertEqual(
            GoogleProvider.output_suffix_for("gemini-2.5-pro-preview-tts"),
            ".wav",
        )

    def test_uses_default_pcm_and_writes_wav_for_flash(self) -> None:
        calls: dict[str, object] = {}
        pcm = b"\x01\x00\x02\x00"

        class FakeInteractions:
            def create(self, **kwargs: object):
                calls.update(kwargs)
                return SimpleNamespace(
                    output_audio=SimpleNamespace(
                        data=base64.b64encode(pcm).decode("ascii"),
                        mime_type="audio/l16;rate=24000",
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
                model="gemini-2.5-flash-preview-tts",
                document=parse("Пример."),
                output=output,
            )
            with wave.open(str(output), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 1)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertEqual(wav_file.getframerate(), 24_000)
                self.assertEqual(wav_file.readframes(wav_file.getnframes()), pcm)
            self.assertEqual(result, output.resolve())

        self.assertEqual(calls["api_key"], "secret")
        self.assertEqual(calls["model"], "gemini-2.5-flash-preview-tts")
        self.assertEqual(
            calls["response_format"],
            {"type": "audio"},
        )
        self.assertEqual(
            calls["generation_config"], {"speech_config": [{"voice": "Kore"}]}
        )
        self.assertIn("TRANSCRIPT:\nПример.", calls["input"])

    def test_uses_default_pcm_and_writes_wav_for_pro(self) -> None:
        calls: dict[str, object] = {}
        pcm = b"\x03\x00\x04\x00"

        class FakeInteractions:
            def create(self, **kwargs: object):
                calls.update(kwargs)
                return SimpleNamespace(
                    output_audio=SimpleNamespace(
                        data=base64.b64encode(pcm).decode("ascii"),
                        mime_type="audio/l16;rate=24000",
                    )
                )

        class FakeClient:
            def __init__(self, *, api_key: str) -> None:
                self.interactions = FakeInteractions()

        provider = GoogleProvider(
            api_key="secret", voice="Kore", client_factory=FakeClient
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "sample.wav")
            provider.synthesize(
                model="gemini-2.5-pro-preview-tts",
                document=parse("Test."),
                output=output,
            )
            with wave.open(str(output), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 1)
                self.assertEqual(wav_file.getsampwidth(), 2)
                self.assertEqual(wav_file.getframerate(), 24_000)
                self.assertEqual(wav_file.readframes(wav_file.getnframes()), pcm)

        self.assertEqual(
            calls["response_format"],
            {"type": "audio"},
        )

    def test_flash_requires_wav_output(self) -> None:
        provider = GoogleProvider(
            api_key="secret", voice="Kore", client_factory=lambda **_: None
        )
        with self.assertRaisesRegex(ProviderError, r"\.wav"):
            provider.synthesize(
                model="gemini-2.5-flash-preview-tts",
                document=parse("Пример."),
                output=Path("sample.mp3"),
            )

    def test_pro_requires_wav_output(self) -> None:
        provider = GoogleProvider(
            api_key="secret", voice="Kore", client_factory=lambda **_: None
        )
        with self.assertRaisesRegex(ProviderError, r"\.wav"):
            provider.synthesize(
                model="gemini-2.5-pro-preview-tts",
                document=parse("Test."),
                output=Path("sample.mp3"),
            )

    def test_rejects_an_unexpected_audio_format(self) -> None:
        class FakeInteractions:
            def create(self, **kwargs: object):
                return SimpleNamespace(
                    output_audio=SimpleNamespace(
                        data=base64.b64encode(b"ID3audio").decode("ascii"),
                        mime_type="audio/mp3",
                    )
                )

        class FakeClient:
            def __init__(self, *, api_key: str) -> None:
                self.interactions = FakeInteractions()

        provider = GoogleProvider(
            api_key="secret", voice="Kore", client_factory=FakeClient
        )
        with tempfile.TemporaryDirectory() as directory, self.assertRaisesRegex(
            ProviderError, "expected the default PCM format"
        ):
            provider.synthesize(
                model="gemini-2.5-flash-preview-tts",
                document=parse("Пример."),
                output=Path(directory, "sample.wav"),
            )


if __name__ == "__main__":
    unittest.main()
