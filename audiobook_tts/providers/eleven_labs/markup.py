from __future__ import annotations

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

_PAUSE_TAGS = {
    "short": "[short pause]",
    "medium": "[pause]",
    "long": "[long pause]",
}


def compile_document(document: Document) -> str:
    """Render a provider-neutral ABM document as Eleven v3 input."""

    rendered_blocks: list[str] = []
    for block in document.blocks:
        if isinstance(block, (Heading, Paragraph)):
            rendered_blocks.append("".join(_compile_inline(node) for node in block.content))

    return "\n\n".join(rendered_blocks).strip()


def _compile_inline(node: Inline) -> str:
    if isinstance(node, Text):
        return node.value
    if isinstance(node, Emphasis):
        # Eleven v3 uses capitalization as its documented emphasis mechanism.
        return node.value.upper()
    if isinstance(node, Pause):
        return _PAUSE_TAGS[node.length]
    if isinstance(node, SayAs):
        return node.spoken
    raise TypeError(f"Unsupported ABM node: {type(node).__name__}")
