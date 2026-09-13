from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audiobook_tts.config import (
    DEFAULT_ELEVENLABS_VOICE_ID,
    ConfigurationError,
    load_settings,
)


class SettingsTests(unittest.TestCase):
    def test_loads_values_from_dotenv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, ".env").write_text(
                "ELEVENLABS_API_KEY=test-key\nELEVENLABS_VOICE_ID=test-voice\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True), patch(
                "pathlib.Path.cwd", return_value=Path(directory)
            ):
                settings = load_settings()

        self.assertEqual(settings.elevenlabs_api_key, "test-key")
        self.assertEqual(settings.elevenlabs_voice_id, "test-voice")

    def test_reports_missing_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory, patch.dict(
            os.environ, {}, clear=True
        ), patch("pathlib.Path.cwd", return_value=Path(directory)):
            with self.assertRaisesRegex(ConfigurationError, "ELEVENLABS_API_KEY"):
                load_settings()

    def test_uses_default_voice_when_voice_id_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, ".env").write_text(
                "ELEVENLABS_API_KEY=test-key\nELEVENLABS_VOICE_ID=\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True), patch(
                "pathlib.Path.cwd", return_value=Path(directory)
            ):
                settings = load_settings()

        self.assertEqual(settings.elevenlabs_voice_id, DEFAULT_ELEVENLABS_VOICE_ID)

    def test_voice_override_takes_precedence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, ".env").write_text(
                "ELEVENLABS_API_KEY=test-key\nELEVENLABS_VOICE_ID=env-voice\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True), patch(
                "pathlib.Path.cwd", return_value=Path(directory)
            ):
                settings = load_settings(voice_id_override="cli-voice")

        self.assertEqual(settings.elevenlabs_voice_id, "cli-voice")


if __name__ == "__main__":
    unittest.main()
