from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from audiobook_tts.markup import parse
from audiobook_tts.providers import ProviderError
from audiobook_tts.providers.eleven_labs import ElevenLabsProvider


class ProviderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.provider = ElevenLabsProvider(api_key="key", voice_id="voice")

    def test_rejects_unsupported_model_before_api_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ProviderError, "Unsupported model"):
                self.provider.synthesize(
                    model="unknown",
                    document=parse("Текст"),
                    output=Path(directory, "out.mp3"),
                )

    def test_rejects_text_over_model_limit_before_api_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ProviderError, "5,001 characters"):
                self.provider.synthesize(
                    model="eleven_v3",
                    document=parse("а" * 5_001),
                    output=Path(directory, "out.mp3"),
                )

    def test_writes_byte_iterable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "out.mp3")
            self.provider._write_audio(output, iter([b"abc", b"", b"def"]))
            self.assertEqual(output.read_bytes(), b"abcdef")

    def test_calls_sdk_and_writes_result(self) -> None:
        calls: dict[str, object] = {}

        class FakeTextToSpeech:
            def convert(self, **kwargs: object):
                calls.update(kwargs)
                return iter([b"audio-data"])

        class FakeClient:
            def __init__(self, *, api_key: str) -> None:
                calls["api_key"] = api_key
                self.text_to_speech = FakeTextToSpeech()

        provider = ElevenLabsProvider(
            api_key="secret",
            voice_id="russian-voice",
            client_factory=FakeClient,
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "sample.mp3")
            result = provider.synthesize(
                model="eleven_v3",
                document=parse("Пример: **важно**. {{pause:short}}"),
                output=output,
            )

            self.assertEqual(output.read_bytes(), b"audio-data")
            self.assertEqual(result, output.resolve())

        self.assertEqual(
            calls,
            {
                "api_key": "secret",
                "voice_id": "russian-voice",
                "text": "Пример: ВАЖНО. [short pause]",
                "model_id": "eleven_v3",
                "output_format": "mp3_44100_128",
            },
        )

    def test_compiles_pause_inside_emphasis_without_altering_cue(self) -> None:
        calls: dict[str, object] = {}

        class FakeTextToSpeech:
            def convert(self, **kwargs: object):
                calls.update(kwargs)
                return iter([b"audio-data"])

        class FakeClient:
            def __init__(self, *, api_key: str) -> None:
                self.text_to_speech = FakeTextToSpeech()

        provider = ElevenLabsProvider(
            api_key="secret",
            voice_id="russian-voice",
            client_factory=FakeClient,
        )
        with tempfile.TemporaryDirectory() as directory:
            provider.synthesize(
                model="eleven_v3",
                document=parse("**текст {{pause:short}}**"),
                output=Path(directory, "sample.mp3"),
            )

        self.assertEqual(calls["text"], "ТЕКСТ [short pause]")


if __name__ == "__main__":
    unittest.main()
