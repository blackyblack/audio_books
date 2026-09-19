from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TypeAlias


class MarkupError(ValueError):
    """Raised when Audiobook Markdown is malformed or unsupported."""


DEFAULT_NARRATOR_STYLE = (
    "Clear and neutral audiobook narration with natural pacing and restrained "
    "expression."
)


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


@dataclass(frozen=True)
class Cue:
    name: str


Inline: TypeAlias = Text | Emphasis | Pause | SayAs | Cue


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
    narrator_style: str | None = None


_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
_NARRATOR_STYLE_RE = re.compile(r"^\s*\{\{narrator-style:([^{}]+)\}\}\s*$")
# A conservative, audiobook-oriented subset of Gemini's documented audio tags.
# Kebab-case is used where Gemini's tag contains spaces so ABM directives remain
# easy to parse and portable to other providers.
SUPPORTED_CUES = frozenset(
    {
        "amazed",
        "bored",
        "crying",
        "curious",
        "excited",
        "excitedly",
        "gasp",
        "giggles",
        "laughs",
        "mischievously",
        "panicked",
        "reluctantly",
        "sarcastic",
        "serious",
        "shouting",
        "sighs",
        "tired",
        "trembling",
        "very-fast",
        "very-slow",
        "whispers",
    }
)

_INLINE_TOKEN_RE = re.compile(
    r"\*\*(?P<emphasis>.+?)\*\*"
    r"|\{\{pause:(?P<pause>short|medium|long)\}\}"
    r"|\{\{say:(?P<say_display>[^{}|]+)\|(?P<say_spoken>[^{}]+)\}\}"
    r"|\{\{cue:(?P<cue>[a-z]+(?:-[a-z]+)*)\}\}"
)


def parse(source: str) -> Document:
    """Parse provider-independent Audiobook Markdown."""

    if not source or not source.strip():
        raise MarkupError("Input text must not be empty.")

    normalized = source.replace("\r\n", "\n").replace("\r", "\n").strip()
    blocks: list[Block] = []
    paragraph_lines: list[str] = []
    narrator_style: str | None = None
    seen_spoken_content = False

    def flush_paragraph() -> None:
        if paragraph_lines:
            blocks.append(Paragraph(content=_parse_inline("\n".join(paragraph_lines))))
            paragraph_lines.clear()

    for line in normalized.split("\n"):
        if not line.strip():
            flush_paragraph()
            continue

        style = _NARRATOR_STYLE_RE.fullmatch(line)
        if style:
            if seen_spoken_content or paragraph_lines or blocks:
                raise MarkupError(
                    "Narrator style must appear in the ABM preamble."
                )
            if narrator_style is not None:
                raise MarkupError(
                    "ABM may contain only one narrator-style directive."
                )
            narrator_style = style.group(1).strip()
            if not narrator_style:
                raise MarkupError("Narrator style must not be empty.")
            continue

        heading = _HEADING_RE.fullmatch(line)
        if heading:
            flush_paragraph()
            seen_spoken_content = True
            blocks.append(
                Heading(
                    level=len(heading.group(1)),
                    content=_parse_inline(heading.group(2)),
                )
            )
        else:
            seen_spoken_content = True
            paragraph_lines.append(line)

    flush_paragraph()

    if not blocks:
        raise MarkupError("Input text must contain spoken content.")

    return Document(blocks=tuple(blocks), narrator_style=narrator_style)


def _parse_inline(value: str) -> tuple[Inline, ...]:
    nodes: list[Inline] = []
    position = 0

    for match in _INLINE_TOKEN_RE.finditer(value):
        plain = value[position : match.start()]
        if plain:
            nodes.append(Text(plain))

        if match.group("emphasis") is not None:
            emphasized = match.group("emphasis").strip()
            if not emphasized:
                raise MarkupError("Emphasis must not be empty.")
            nodes.append(
                Emphasis(content=_parse_inline(emphasized))
            )
        elif match.group("pause") is not None:
            nodes.append(Pause(match.group("pause")))
        elif match.group("say_display") is not None:
            display = match.group("say_display").strip()
            spoken = match.group("say_spoken").strip()
            if not display or not spoken:
                raise MarkupError("Both forms in a say directive must not be empty.")
            nodes.append(SayAs(display=display, spoken=spoken))
        else:
            cue = match.group("cue")
            if cue not in SUPPORTED_CUES:
                supported = ", ".join(sorted(SUPPORTED_CUES))
                raise MarkupError(
                    f"Unsupported ABM cue '{cue}'. Supported cues: {supported}."
                )
            nodes.append(Cue(name=cue))
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
            "{{pause:short|medium|long}}, {{say:display|spoken}}, and "
            "{{cue:name}}, and {{narrator-style:description}}."
        )
    if "**" in text_outside_tokens or value.count("**") % 2:
        raise MarkupError("Unclosed or malformed emphasis marker '**'.")
