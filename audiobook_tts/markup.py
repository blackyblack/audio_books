from __future__ import annotations

import re


class MarkupError(ValueError):
    """Raised when Audiobook Markdown is malformed or unsupported."""


_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
_SAY_RE = re.compile(r"\{\{say:([^{}|]+)\|([^{}]+)\}\}")
_PAUSE_RE = re.compile(r"\{\{pause:(short|medium|long)\}\}")
_EMPHASIS_RE = re.compile(r"\*\*(.+?)\*\*")

_PAUSE_TAGS = {
    "short": "[short pause]",
    "medium": "[pause]",
    "long": "[long pause]",
}


def compile_for_elevenlabs(source: str) -> str:
    """Compile the small ABM v0 subset to Eleven v3-compatible text cues."""

    if not source or not source.strip():
        raise MarkupError("Input text must not be empty.")

    normalized = source.replace("\r\n", "\n").replace("\r", "\n")
    lines: list[str] = []
    for line in normalized.split("\n"):
        heading = _HEADING_RE.match(line)
        lines.append(heading.group(1) if heading else line)

    compiled = "\n".join(lines)
    compiled = _SAY_RE.sub(lambda match: match.group(2).strip(), compiled)
    compiled = _PAUSE_RE.sub(lambda match: _PAUSE_TAGS[match.group(1)], compiled)

    if compiled.count("**") % 2:
        raise MarkupError("Unclosed emphasis marker '**'.")
    # Eleven v3's documented emphasis mechanism is capitalization. Keeping
    # this provider-specific choice here leaves ABM's semantics provider-neutral.
    compiled = _EMPHASIS_RE.sub(
        lambda match: match.group(1).strip().upper(), compiled
    )

    if "{{" in compiled or "}}" in compiled:
        raise MarkupError(
            "Unknown or malformed ABM directive. Supported directives are "
            "{{pause:short|medium|long}} and {{say:display|spoken}}."
        )

    return compiled.strip()
