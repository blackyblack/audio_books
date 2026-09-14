from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audiobook_tts.config import ConfigurationError
from audiobook_tts.providers.google.config import (
    DEFAULT_VOICE as GOOGLE_DEFAULT_VOICE,
)
from audiobook_tts.providers.google.config import load_settings as load_google_settings
from audiobook_tts.providers.yandex.config import (
    DEFAULT_VOICE as YANDEX_DEFAULT_VOICE,
)
from audiobook_tts.providers.yandex.config import load_settings as load_yandex_settings


class ProviderConfigTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
