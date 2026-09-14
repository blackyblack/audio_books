from __future__ import annotations

import contextlib
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from audiobook_tts.corpus import load_corpus
from audiobook_tts.corpus_cli import run_corpus
from audiobook_tts.markup import Document


CORPUS_ROOT = Path(__file__).parents[1] / "corpus"


class FakeProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Document, Path]] = []

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path:
        self.calls.append((model, document, output))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"audio")
        return output


class CorpusRunnerTests(unittest.TestCase):
    def test_loads_every_manifest_entry(self) -> None:
        samples = load_corpus(CORPUS_ROOT)

        self.assertEqual(len(samples), 15)
        self.assertEqual(samples[0].group, "short")
        self.assertEqual(samples[-1].group, "continuity")

    def test_generates_all_samples_then_skips_existing_outputs(self) -> None:
        samples = load_corpus(CORPUS_ROOT)
        provider = FakeProvider()

        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(
            StringIO()
        ):
            output_dir = Path(directory)
            generated, skipped = run_corpus(
                provider=provider,
                model="test-model",
                samples=samples,
                output_dir=output_dir,
            )
            generated_again, skipped_again = run_corpus(
                provider=provider,
                model="test-model",
                samples=samples,
                output_dir=output_dir,
            )

            expected_output = output_dir / samples[0].relative_path.with_suffix(".mp3")
            self.assertEqual(expected_output.read_bytes(), b"audio")

        self.assertEqual((generated, skipped), (15, 0))
        self.assertEqual((generated_again, skipped_again), (0, 15))
        self.assertEqual(len(provider.calls), 15)


if __name__ == "__main__":
    unittest.main()
