from __future__ import annotations

from html import escape

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

_PAUSE_LENGTHS = {"short": "150ms", "medium": "400ms", "long": "900ms"}


def compile_document(document: Document) -> str:
    """Render provider-neutral ABM as Chirp 3 HD SSML."""

    blocks = []
    for block in document.blocks:
        if isinstance(block, (Heading, Paragraph)):
            content_parts: list[str] = []
            for node in block.content:
                content_parts.append(_compile_inline(node))
            content = "".join(content_parts)
            blocks.append(f"<p>{content}</p>")
    return f"<speak>{''.join(blocks)}</speak>"


def _compile_inline(node: Inline) -> str:
    if isinstance(node, Text):
        return escape(node.value, quote=False)
    if isinstance(node, Emphasis):
        content = "".join(_compile_inline(child) for child in node.content)
        return f'<prosody volume="loud">{content}</prosody>'
    if isinstance(node, Pause):
        return f'<break time="{_PAUSE_LENGTHS[node.length]}"/>'
    if isinstance(node, SayAs):
        alias = escape(node.spoken, quote=True)
        display = escape(node.display, quote=False)
        return f'<sub alias="{alias}">{display}</sub>'
    if isinstance(node, Cue):
        # Chirp has no inline emotional-direction syntax.
        return ""
    raise TypeError(f"Unsupported ABM node: {type(node).__name__}")
