from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Protocol

from audiobook_tts.config import ConfigurationError, load_environment
from audiobook_tts.corpus import CorpusDocument, CorpusError, load_corpus
from audiobook_tts.markup import Document
from audiobook_tts.providers import ProviderError
from audiobook_tts.providers.factory import SUPPORTED_MODELS, create_provider


class CorpusProvider(Protocol):
    OUTPUT_SUFFIX: str

    def synthesize(self, *, model: str, document: Document, output: Path) -> Path: ...


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audiobook-tts-corpus",
        description="Generate audio for every sample in the evaluation corpus.",
    )
    parser.add_argument(
        "--model",
        required=True,
        choices=sorted(SUPPORTED_MODELS),
        help="TTS model to use for every sample.",
    )
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=Path("corpus"),
        help="Corpus directory containing manifest.json (default: corpus).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output root (default: outputs/<model>).",
    )
    parser.add_argument(
        "--voice-id",
        help="Override the provider's configured voice for this corpus run.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate existing output files. This may incur repeat charges.",
    )
    return parser


def run_corpus(
    *,
    provider: CorpusProvider,
    model: str,
    samples: tuple[CorpusDocument, ...],
    output_dir: Path,
    overwrite: bool = False,
    output_suffix: str = ".mp3",
) -> tuple[int, int]:
    """Generate all prepared samples and return generated and skipped counts."""

    generated = 0
    skipped = 0
    total = len(samples)

    for index, sample in enumerate(samples, start=1):
        output = output_dir / sample.relative_path.with_suffix(output_suffix)
        if output.exists() and not overwrite:
            print(f"[{index}/{total}] Skipping existing {output}")
            skipped += 1
            continue

        print(f"[{index}/{total}] Generating {sample.id} -> {output}")
        provider.synthesize(model=model, document=sample.document, output=output)
        generated += 1

    return generated, skipped


def main(argv: list[str] | None = None) -> int:
    load_environment()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        # Validate and parse the complete corpus before the first billable call.
        samples = load_corpus(args.corpus_root)
        provider = create_provider(model=args.model, voice_id_override=args.voice_id)
        output_dir = args.output_dir or Path("outputs") / args.model
        generated, skipped = run_corpus(
            provider=provider,
            model=args.model,
            samples=samples,
            output_dir=output_dir,
            overwrite=args.overwrite,
            output_suffix=provider.OUTPUT_SUFFIX,
        )
    except (ConfigurationError, CorpusError, ProviderError) as exc:
        parser.exit(2, f"error: {exc}\n")

    print(f"Corpus run complete: {generated} generated, {skipped} skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
