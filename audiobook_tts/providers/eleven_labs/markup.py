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
    SUPPORTED_CUES,
    Text,
)

_PAUSE_TAGS = {
    "short": "[short pause]",
    "medium": "[pause]",
    "long": "[long pause]",
}

_CUE_TAGS = {name: f"[{name}]" for name in SUPPORTED_CUES} | {
    "very-fast": "[very fast]",
    "very-slow": "[very slow]",
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
        return "".join(_compile_emphasized(child) for child in node.content)
    if isinstance(node, Pause):
        return _PAUSE_TAGS[node.length]
    if isinstance(node, SayAs):
        return node.spoken
    if isinstance(node, Cue):
        return _CUE_TAGS[node.name]
    raise TypeError(f"Unsupported ABM node: {type(node).__name__}")


def _compile_emphasized(node: Inline) -> str:
    if isinstance(node, Text):
        return node.value.upper()
    if isinstance(node, Emphasis):
        return "".join(_compile_emphasized(child) for child in node.content)
    if isinstance(node, Pause):
        return _PAUSE_TAGS[node.length]
    if isinstance(node, SayAs):
        return node.spoken.upper()
    if isinstance(node, Cue):
        return _CUE_TAGS[node.name]
    raise TypeError(f"Unsupported ABM node: {type(node).__name__}")
