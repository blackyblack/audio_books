from __future__ import annotations

from audiobook_tts.markup import (
    Cue,
    Document,
    Emphasis,
    Heading,
    Inline,
    Paragraph,
    Pause,
    SayAs,
    Text,
)

_PAUSES = {"short": ", ", "medium": "… ", "long": "… … "}


def compile_document(document: Document) -> str:
    """Render ABM as plain transcript text accepted by Qwen TTS."""

    blocks = []
    for block in document.blocks:
        if isinstance(block, (Heading, Paragraph)):
            blocks.append("".join(_compile_inline(node) for node in block.content))
    return "\n\n".join(blocks).strip()


def _compile_inline(node: Inline) -> str:
    if isinstance(node, Text):
        return node.value
    if isinstance(node, Emphasis):
        return "".join(_compile_inline(child) for child in node.content)
    if isinstance(node, Pause):
        return _PAUSES[node.length]
    if isinstance(node, SayAs):
        return node.spoken
    if isinstance(node, Cue):
        return ""
    raise TypeError(f"Unsupported ABM node: {type(node).__name__}")
