from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from audiobook_tts.markup import parse
from audiobook_tts.providers import ProviderError
from audiobook_tts.providers.chirp3 import Chirp3Provider


class Chirp3ProviderTests(unittest.TestCase):
    def test_synthesizes_russian_ssml_as_mp3(self) -> None:
        calls: dict[str, object] = {}

        class FakeClient:
            def synthesize_speech(self, *, request: object):
                calls["request"] = request
                return SimpleNamespace(audio_content=b"ID3audio")

        provider = Chirp3Provider(
            voice="ru-RU-Chirp3-HD-Kore", client_factory=FakeClient
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "sample.mp3")
            result = provider.synthesize(
                model="chirp3-hd", document=parse("Пример."), output=output
            )

            self.assertEqual(output.read_bytes(), b"ID3audio")
            self.assertEqual(result, output.resolve())

        request = calls["request"]
        self.assertEqual(request["voice"]["language_code"], "ru-RU")
        self.assertEqual(request["voice"]["name"], "ru-RU-Chirp3-HD-Kore")
        self.assertEqual(request["audio_config"], {"audio_encoding": "MP3"})
        self.assertEqual(request["input"], {"ssml": "<speak><p>Пример.</p></speak>"})

    def test_rejects_wrong_output_extension(self) -> None:
        provider = Chirp3Provider(voice="ru-RU-Chirp3-HD-Kore")
        with self.assertRaisesRegex(ProviderError, r"\.mp3"):
            provider.synthesize(
                model="chirp3-hd", document=parse("Пример."), output=Path("x.wav")
            )

if __name__ == "__main__":
    unittest.main()
