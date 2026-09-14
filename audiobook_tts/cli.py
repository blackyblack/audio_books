from __future__ import annotations

import argparse
import sys
from pathlib import Path

from audiobook_tts.config import ConfigurationError, load_environment
from audiobook_tts.markup import MarkupError, parse
from audiobook_tts.providers import ProviderError
from audiobook_tts.providers.factory import SUPPORTED_MODELS, create_provider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="audiobook-tts",
        description="Generate a Russian audiobook sample with a selected TTS model.",
    )
    parser.add_argument(
        "--model",
        required=True,
        choices=sorted(SUPPORTED_MODELS),
        help="TTS model to use.",
    )
    text_source = parser.add_mutually_exclusive_group(required=True)
    text_source.add_argument("--text", help="Input text or Audiobook Markdown.")
    text_source.add_argument(
        "--input-file",
        type=Path,
        help="Read input text or Audiobook Markdown from a UTF-8 file.",
    )
    parser.add_argument(
        "--voice-id",
        help="Override the selected provider's configured voice for this request.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output MP3 path (default: output.mp3).",
    )
    return parser


def read_input(*, text: str | None, input_file: Path | None) -> str:
    if text is not None:
        return text
    assert input_file is not None
    try:
        return input_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"Could not read UTF-8 input file '{input_file}': {exc}") from exc


def run(args: argparse.Namespace) -> Path:
    source = read_input(text=args.text, input_file=args.input_file)
    document = parse(source)
    provider = create_provider(model=args.model, voice_id_override=args.voice_id)
    output = args.output or Path(f"output{provider.OUTPUT_SUFFIX}")
    return provider.synthesize(model=args.model, document=document, output=output)


def main(argv: list[str] | None = None) -> int:
    load_environment()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        output = run(args)
    except (ConfigurationError, MarkupError, ProviderError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")

    print(f"Audio written to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
