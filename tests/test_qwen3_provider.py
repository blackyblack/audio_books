from __future__ import annotations

import io
import tempfile
import unittest
import wave
from pathlib import Path

from audiobook_tts.markup import parse
from audiobook_tts.providers import ProviderError
from audiobook_tts.providers.qwen3 import Qwen3Provider


MODEL = "qwen3-tts-vd-2026-01-26"


def make_wav(frames: bytes) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(24_000)
        audio.writeframes(frames)
    return buffer.getvalue()


class FakeResponse:
    def __init__(self, *, body: object | None = None, content: bytes = b"") -> None:
        self._body = body
        self.content = content

    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return self._body


class FakeSession:
    def __init__(self) -> None:
        self.posts: list[dict[str, object]] = []
        self.gets: list[str] = []
        self.synthesis_count = 0

    def __enter__(self):
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        call = {"url": url, **kwargs}
        self.posts.append(call)
        if call["json"]["model"] == "qwen-voice-design":
            return FakeResponse(body={"output": {"voice": "vd-audiobook-123"}})

        self.synthesis_count += 1
        return FakeResponse(
            body={
                "output": {
                    "audio": {"url": f"https://audio/{self.synthesis_count}"}
                }
            }
        )

    def get(self, url: str, **kwargs: object) -> FakeResponse:
        self.gets.append(url)
        index = len(self.gets)
        return FakeResponse(content=make_wav(bytes([index, 0])))


class Qwen3ProviderTests(unittest.TestCase):
    def test_creates_voice_then_synthesizes_and_caches_it(self) -> None:
        session = FakeSession()
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory, "voice-id")
            provider = self._provider(session=session, voice=None, cache=cache)
            output = Path(directory, "sample.wav")
            result = provider.synthesize(
                model=MODEL,
                document=parse("{{cue:whispers}}Пример."),
                output=output,
            )
            with wave.open(str(output), "rb") as audio:
                self.assertEqual(audio.getframerate(), 24_000)
                self.assertEqual(audio.readframes(audio.getnframes()), b"\x01\x00")
            self.assertEqual(result, output.resolve())
            self.assertEqual(cache.read_text(encoding="utf-8").strip(), "vd-audiobook-123")

        voice_call, synthesis_call = session.posts
        self.assertTrue(voice_call["url"].endswith("/services/audio/tts/customization"))
        voice_request = voice_call["json"]
        self.assertEqual(voice_request["model"], "qwen-voice-design")
        self.assertEqual(voice_request["input"]["target_model"], MODEL)
        self.assertEqual(voice_request["input"]["voice_prompt"], "Warm narrator")
        self.assertIn("preview_text", voice_request["input"])

        self.assertTrue(
            synthesis_call["url"].endswith(
                "/services/aigc/multimodal-generation/generation"
            )
        )
        request = synthesis_call["json"]
        self.assertEqual(request["model"], MODEL)
        self.assertEqual(request["input"], {"text": "Пример.", "voice": "vd-audiobook-123"})

    def test_configured_voice_skips_voice_creation(self) -> None:
        session = FakeSession()
        with tempfile.TemporaryDirectory() as directory:
            provider = self._provider(
                session=session,
                voice="vd-existing-voice",
                cache=Path(directory, "missing-cache"),
            )
            provider.synthesize(
                model=MODEL,
                document=parse("Пример."),
                output=Path(directory, "sample.wav"),
            )

        self.assertEqual(len(session.posts), 1)
        self.assertEqual(
            session.posts[0]["json"]["input"]["voice"], "vd-existing-voice"
        )

    def test_cached_voice_skips_voice_creation(self) -> None:
        session = FakeSession()
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory, "voice-id")
            cache.write_text("vd-cached-voice\n", encoding="utf-8")
            provider = self._provider(session=session, voice=None, cache=cache)
            provider.synthesize(
                model=MODEL,
                document=parse("Пример."),
                output=Path(directory, "sample.wav"),
            )

        self.assertEqual(len(session.posts), 1)
        self.assertEqual(
            session.posts[0]["json"]["input"]["voice"], "vd-cached-voice"
        )

    def test_splits_long_input_and_joins_wav_responses(self) -> None:
        session = FakeSession()
        with tempfile.TemporaryDirectory() as directory:
            provider = self._provider(
                session=session,
                voice="vd-existing-voice",
                cache=Path(directory, "voice-id"),
            )
            output = Path(directory, "sample.wav")
            provider.synthesize(
                model=MODEL,
                document=parse("я" * 601),
                output=output,
            )
            with wave.open(str(output), "rb") as audio:
                self.assertEqual(
                    audio.readframes(audio.getnframes()), b"\x01\x00\x02\x00"
                )

        self.assertEqual(len(session.posts), 2)
        lengths = [len(call["json"]["input"]["text"]) for call in session.posts]
        self.assertEqual(lengths, [600, 1])

    def test_rejects_wrong_output_extension(self) -> None:
        provider = Qwen3Provider(
            api_key="secret",
            voice="vd-existing-voice",
            base_url="https://example.test",
            voice_prompt="Warm narrator",
            voice_cache=Path("voice-id"),
        )
        with self.assertRaisesRegex(ProviderError, r"\.wav"):
            provider.synthesize(
                model=MODEL,
                document=parse("Пример."),
                output=Path("sample.mp3"),
            )

    @staticmethod
    def _provider(*, session: FakeSession, voice: str | None, cache: Path) -> Qwen3Provider:
        return Qwen3Provider(
            api_key="secret",
            voice=voice,
            base_url="https://dashscope.example/api/v1/",
            voice_prompt="Warm narrator",
            voice_cache=cache,
            session_factory=lambda: session,
        )


if __name__ == "__main__":
    unittest.main()
