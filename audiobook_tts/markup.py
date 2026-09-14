from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TypeAlias


class MarkupError(ValueError):
    """Raised when Audiobook Markdown is malformed or unsupported."""


@dataclass(frozen=True)
class Text:
    value: str


@dataclass(frozen=True)
class Emphasis:
    content: tuple[Inline, ...]


@dataclass(frozen=True)
class Pause:
    length: str


@dataclass(frozen=True)
class SayAs:
    display: str
    spoken: str


Inline: TypeAlias = Text | Emphasis | Pause | SayAs


@dataclass(frozen=True)
class Heading:
    level: int
    content: tuple[Inline, ...]


@dataclass(frozen=True)
class Paragraph:
    content: tuple[Inline, ...]


Block: TypeAlias = Heading | Paragraph


@dataclass(frozen=True)
class Document:
    blocks: tuple[Block, ...]


_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
_INLINE_TOKEN_RE = re.compile(
    r"\*\*(.+?)\*\*"
    r"|\{\{pause:(short|medium|long)\}\}"
    r"|\{\{say:([^{}|]+)\|([^{}]+)\}\}"
)


def parse(source: str) -> Document:
    """Parse the provider-independent Audiobook Markdown v0 subset."""

    if not source or not source.strip():
        raise MarkupError("Input text must not be empty.")

    normalized = source.replace("\r\n", "\n").replace("\r", "\n").strip()
    blocks: list[Block] = []
    paragraph_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph_lines:
            blocks.append(Paragraph(content=_parse_inline("\n".join(paragraph_lines))))
            paragraph_lines.clear()

    for line in normalized.split("\n"):
        if not line.strip():
            flush_paragraph()
            continue

        heading = _HEADING_RE.fullmatch(line)
        if heading:
            flush_paragraph()
            blocks.append(
                Heading(
                    level=len(heading.group(1)),
                    content=_parse_inline(heading.group(2)),
                )
            )
        else:
            paragraph_lines.append(line)

    flush_paragraph()

    return Document(blocks=tuple(blocks))


def _parse_inline(value: str) -> tuple[Inline, ...]:
    nodes: list[Inline] = []
    position = 0

    for match in _INLINE_TOKEN_RE.finditer(value):
        plain = value[position : match.start()]
        if plain:
            nodes.append(Text(plain))

        if match.group(1) is not None:
            emphasized = match.group(1).strip()
            if not emphasized:
                raise MarkupError("Emphasis must not be empty.")
            nodes.append(Emphasis(content=_parse_inline(emphasized)))
        elif match.group(2) is not None:
            nodes.append(Pause(match.group(2)))
        else:
            display = match.group(3).strip()
            spoken = match.group(4).strip()
            if not display or not spoken:
                raise MarkupError("Both forms in a say directive must not be empty.")
            nodes.append(SayAs(display=display, spoken=spoken))

        position = match.end()

    remainder = value[position:]
    if remainder:
        nodes.append(Text(remainder))

    _reject_unparsed_markup(value, nodes)
    return tuple(nodes)


def _reject_unparsed_markup(value: str, nodes: list[Inline]) -> None:
    text_outside_tokens = "".join(
        node.value for node in nodes if isinstance(node, Text)
    )
    if "{{" in text_outside_tokens or "}}" in text_outside_tokens:
        raise MarkupError(
            "Unknown or malformed ABM directive. Supported directives are "
            "{{pause:short|medium|long}} and {{say:display|spoken}}."
        )
    if "**" in text_outside_tokens or value.count("**") % 2:
        raise MarkupError("Unclosed or malformed emphasis marker '**'.")
