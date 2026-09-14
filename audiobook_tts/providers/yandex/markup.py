from __future__ import annotations

import re

from audiobook_tts.markup import (
    Document,
    Emphasis,
    Heading,
    Inline,
    Paragraph,
    Pause,
    SayAs,
    Text,
)

_STRESSED_VOWEL_RE = re.compile(r"([АЕЁИОУЫЭЮЯаеёиоуыэюя])\N{COMBINING ACUTE ACCENT}")
_PAUSE_TAGS = {
    "short": "sil<[150]>",
    "medium": "sil<[400]>",
    "long": "sil<[900]>",
}


def compile_document(document: Document) -> str:
    """Render provider-neutral ABM as Yandex SpeechKit TTS markup."""

    rendered_blocks: list[str] = []
    for block in document.blocks:
        if isinstance(block, (Heading, Paragraph)):
            rendered_blocks.append("".join(_compile_inline(node) for node in block.content))
    return "\n\n".join(rendered_blocks).strip()


def _compile_inline(node: Inline) -> str:
    if isinstance(node, Text):
        return _convert_stress(node.value)
    if isinstance(node, Emphasis):
        content = "".join(_compile_inline(child) for child in node.content)
        return f"**{content}**"
    if isinstance(node, Pause):
        return _PAUSE_TAGS[node.length]
    if isinstance(node, SayAs):
        return _convert_stress(node.spoken)
    raise TypeError(f"Unsupported ABM node: {type(node).__name__}")


def _convert_stress(value: str) -> str:
    return _STRESSED_VOWEL_RE.sub(r"+\1", value)
