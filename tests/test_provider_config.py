from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audiobook_tts.config import ConfigurationError
from audiobook_tts.providers.chirp3.config import (
    DEFAULT_VOICE as CHIRP3_DEFAULT_VOICE,
)
from audiobook_tts.providers.chirp3.config import load_settings as load_chirp3_settings
from audiobook_tts.providers.google.config import (
    DEFAULT_VOICE as GOOGLE_DEFAULT_VOICE,
)
from audiobook_tts.providers.google.config import load_settings as load_google_settings
from audiobook_tts.providers.qwen3.config import DEFAULT_BASE_URL as QWEN_DEFAULT_BASE_URL
from audiobook_tts.providers.qwen3.config import DEFAULT_VOICE_CACHE
from audiobook_tts.providers.qwen3.config import DEFAULT_VOICE_PROMPT
from audiobook_tts.providers.qwen3.config import load_settings as load_qwen3_settings
from audiobook_tts.providers.yandex.config import (
    DEFAULT_VOICE as YANDEX_DEFAULT_VOICE,
)
from audiobook_tts.providers.yandex.config import load_settings as load_yandex_settings


class ProviderConfigTests(unittest.TestCase):
    def test_chirp3_uses_adc_and_default_voice(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"CHIRP3_VOICE": ""}, clear=True
        ), patch("pathlib.Path.cwd", return_value=Path(directory)):
            settings = load_chirp3_settings()

        self.assertEqual(settings.voice, CHIRP3_DEFAULT_VOICE)

    def test_google_requires_api_key_and_uses_default_voice(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"GOOGLE_API_KEY": "key", "GOOGLE_VOICE": ""}, clear=True
        ), patch("pathlib.Path.cwd", return_value=Path(directory)):
            settings = load_google_settings()

        self.assertEqual(settings.api_key, "key")
        self.assertEqual(settings.voice, GOOGLE_DEFAULT_VOICE)

    def test_yandex_requires_api_key_and_uses_default_voice(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {"YANDEX_API_KEY": "key", "YANDEX_VOICE": ""}, clear=True
        ), patch("pathlib.Path.cwd", return_value=Path(directory)):
            settings = load_yandex_settings()

        self.assertEqual(settings.api_key, "key")
        self.assertEqual(settings.voice, YANDEX_DEFAULT_VOICE)

    def test_qwen3_requires_api_key_and_uses_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ,
            {"DASHSCOPE_API_KEY": "key", "QWEN_VOICE": ""},
            clear=True,
        ), patch("pathlib.Path.cwd", return_value=Path(directory)):
            settings = load_qwen3_settings()

        self.assertEqual(settings.api_key, "key")
        self.assertIsNone(settings.voice)
        self.assertEqual(settings.base_url, QWEN_DEFAULT_BASE_URL)
        self.assertEqual(settings.voice_prompt, DEFAULT_VOICE_PROMPT)
        self.assertEqual(settings.voice_cache, DEFAULT_VOICE_CACHE)

    def test_google_fails_on_first_missing_setting(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {}, clear=True
        ), patch("pathlib.Path.cwd", return_value=Path(directory)):
            with self.assertRaisesRegex(ConfigurationError, "GOOGLE_API_KEY"):
                load_google_settings()

    def test_yandex_fails_on_first_missing_setting(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {}, clear=True
        ), patch("pathlib.Path.cwd", return_value=Path(directory)):
            with self.assertRaisesRegex(ConfigurationError, "YANDEX_API_KEY"):
                load_yandex_settings()

    def test_qwen3_fails_on_missing_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {}, clear=True
        ), patch("pathlib.Path.cwd", return_value=Path(directory)):
            with self.assertRaisesRegex(ConfigurationError, "DASHSCOPE_API_KEY"):
                load_qwen3_settings()


if __name__ == "__main__":
    unittest.main()
