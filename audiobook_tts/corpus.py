from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from audiobook_tts.markup import Document, MarkupError, parse


class CorpusError(ValueError):
    """Raised when an evaluation corpus is missing or malformed."""


@dataclass(frozen=True)
class CorpusDocument:
    id: str
    group: str
    relative_path: Path
    document: Document


def load_corpus(corpus_root: Path) -> tuple[CorpusDocument, ...]:
    """Load and validate every ABM document listed by a corpus manifest."""

    corpus_root = corpus_root.resolve()
    manifest_path = corpus_root / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CorpusError(f"Could not read corpus manifest '{manifest_path}': {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CorpusError(f"Invalid corpus manifest '{manifest_path}': {exc}") from exc

    entries: list[tuple[str, str, str]] = []
    for group in ("short", "long"):
        samples = manifest.get(group)
        if not isinstance(samples, list):
            raise CorpusError(f"Corpus manifest field '{group}' must be a list.")
        for sample in samples:
            if not isinstance(sample, dict):
                raise CorpusError(f"Corpus manifest '{group}' entry must be an object.")
            entries.append((_required_string(sample, "id"), group, _required_string(sample, "file")))

    continuity = manifest.get("continuity")
    if not isinstance(continuity, dict):
        raise CorpusError("Corpus manifest field 'continuity' must be an object.")
    continuity_id = _required_string(continuity, "id")
    parts = continuity.get("parts")
    if not isinstance(parts, list) or not parts:
        raise CorpusError("Corpus continuity 'parts' must be a non-empty list.")
    for index, relative_path in enumerate(parts, start=1):
        if not isinstance(relative_path, str) or not relative_path:
            raise CorpusError("Every corpus continuity part must be a file path.")
        entries.append((f"{continuity_id}-part-{index}", "continuity", relative_path))

    ids = [entry[0] for entry in entries]
    if len(ids) != len(set(ids)):
        raise CorpusError("Corpus sample IDs must be unique.")

    documents: list[CorpusDocument] = []
    for sample_id, group, relative_value in entries:
        relative_path = _safe_relative_path(relative_value)
        source_path = corpus_root / relative_path
        try:
            source = source_path.read_text(encoding="utf-8")
            document = parse(source)
        except (OSError, UnicodeError) as exc:
            raise CorpusError(f"Could not read corpus sample '{source_path}': {exc}") from exc
        except MarkupError as exc:
            raise CorpusError(f"Invalid ABM in corpus sample '{source_path}': {exc}") from exc
        documents.append(
            CorpusDocument(
                id=sample_id,
                group=group,
                relative_path=relative_path,
                document=document,
            )
        )

    return tuple(documents)


def _required_string(mapping: dict[str, object], field: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value:
        raise CorpusError(f"Corpus manifest field '{field}' must be a non-empty string.")
    return value


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise CorpusError(f"Corpus file path must stay inside the corpus: {value}")
    return path
