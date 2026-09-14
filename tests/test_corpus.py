from __future__ import annotations

import json
import unittest
from pathlib import Path

from audiobook_tts.markup import parse
from audiobook_tts.providers.eleven_labs.markup import compile_document
from audiobook_tts.providers.eleven_labs.provider import ElevenLabsProvider


CORPUS_ROOT = Path(__file__).parents[1] / "corpus"


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(
            (CORPUS_ROOT / "manifest.json").read_text(encoding="utf-8")
        )

    def test_manifest_has_expected_sample_groups(self) -> None:
        self.assertEqual(self.manifest["version"], 1)
        self.assertEqual(self.manifest["language"], "ru-RU")
        self.assertEqual(len(self.manifest["short"]), 10)
        self.assertEqual(len(self.manifest["long"]), 3)
        self.assertEqual(len(self.manifest["continuity"]["parts"]), 2)

    def test_sample_ids_are_unique(self) -> None:
        ids = [sample["id"] for group in ("short", "long") for sample in self.manifest[group]]
        ids.append(self.manifest["continuity"]["id"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_short_samples_are_focused_length(self) -> None:
        for sample in self.manifest["short"]:
            source = self._read(sample["file"])
            with self.subTest(sample=sample["id"]):
                self.assertGreaterEqual(len(source), 250)
                self.assertLessEqual(len(source), 600)

    def test_long_samples_are_sustained_length(self) -> None:
        for sample in self.manifest["long"]:
            source = self._read(sample["file"])
            with self.subTest(sample=sample["id"]):
                self.assertGreaterEqual(len(source), 3_000)
                self.assertLessEqual(len(source), 4_200)

    def test_every_sample_parses_and_fits_eleven_v3(self) -> None:
        paths = [
            sample["file"]
            for group in ("short", "long")
            for sample in self.manifest[group]
        ]
        paths.extend(self.manifest["continuity"]["parts"])

        for relative_path in paths:
            source = self._read(relative_path)
            with self.subTest(file=relative_path):
                compiled = compile_document(parse(source))
                self.assertTrue(compiled)
                self.assertLessEqual(
                    len(compiled), ElevenLabsProvider.MAX_CHARACTERS
                )

    @staticmethod
    def _read(relative_path: str) -> str:
        path = CORPUS_ROOT / relative_path
        if not path.is_file():
            raise AssertionError(f"Corpus file does not exist: {path}")
        return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
