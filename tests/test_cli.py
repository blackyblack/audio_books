from __future__ import annotations

import unittest

from audiobook_tts.cli import build_parser
from audiobook_tts.providers.factory import SUPPORTED_MODELS


class CliTests(unittest.TestCase):
    def test_help_lists_every_supported_model_id(self) -> None:
        help_text = build_parser().format_help()

        for model in SUPPORTED_MODELS:
            with self.subTest(model=model):
                self.assertIn(model, help_text)

if __name__ == "__main__":
    unittest.main()
