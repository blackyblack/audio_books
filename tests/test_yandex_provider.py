from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

from audiobook_tts.markup import parse
from audiobook_tts.providers.yandex import YandexProvider


class YandexProviderTests(unittest.TestCase):
    def test_calls_rest_api_and_writes_all_audio_chunks(self) -> None:
        calls: dict[str, object] = {}

        class FakeResponse:
            def raise_for_status(self) -> None:
                pass

            def iter_lines(self):
                for chunk in (b"abc", b"def"):
                    yield json.dumps(
                        {
                            "audioChunk": {
                                "data": base64.b64encode(chunk).decode("ascii")
                            }
                        }
                    ).encode("utf-8")

        class FakeSession:
            def __enter__(self):
                return self

            def __exit__(self, *args: object) -> None:
                pass

            def post(self, url: str, **kwargs: object) -> FakeResponse:
                calls["url"] = url
                calls.update(kwargs)
                return FakeResponse()

        provider = YandexProvider(
            api_key="secret", voice="marina", session_factory=FakeSession
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "sample.mp3")
            result = provider.synthesize(
                model="yandex-speechkit-v3",
                document=parse("Это **ва́жно**. {{pause:short}}"),
                output=output,
            )

            self.assertEqual(output.read_bytes(), b"abcdef")
            self.assertEqual(result, output.resolve())

        self.assertEqual(calls["url"], YandexProvider.API_URL)
        self.assertEqual(calls["headers"], {"Authorization": "Api-Key secret"})
        self.assertEqual(calls["json"]["text"], "Это **в+ажно**. sil<[150]>")
        self.assertEqual(calls["json"]["hints"], [{"voice": "marina"}])
        self.assertEqual(
            calls["json"]["outputAudioSpec"],
            {"containerAudio": {"containerAudioType": "MP3"}},
        )
        self.assertTrue(calls["json"]["unsafeMode"])


if __name__ == "__main__":
    unittest.main()
