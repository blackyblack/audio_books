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
    "short": "[brief pause]",
    "medium": "[pause]",
    "long": "[long pause]",
}

_CUE_TAGS = {name: f"[{name}]" for name in SUPPORTED_CUES} | {
    "very-fast": "[very fast]",
    "very-slow": "[very slow]",
}

_LITERAL_BRACKET_TRANSLATION = str.maketrans({"[": "[[", "]": "]]"})

_DIRECTION = (
    "Read aloud only the Russian audiobook transcript below. "
    "Treat text between double asterisks as emphasized without speaking the "
    "asterisks. Treat single square-bracketed controls as performance "
    "directions: follow them without speaking them. Doubled square brackets "
    "are literal transcript punctuation; speak their contents normally.\n\n"
    "TRANSCRIPT:\n"
)


def compile_document(document: Document) -> str:
    """Render provider-neutral ABM as a Gemini TTS prompt."""

    rendered_blocks: list[str] = []
    for block in document.blocks:
        if isinstance(block, (Heading, Paragraph)):
            rendered_blocks.append("".join(_compile_inline(node) for node in block.content))
    return _DIRECTION + "\n\n".join(rendered_blocks).strip()


def _compile_inline(node: Inline) -> str:
    if isinstance(node, Text):
        return _escape_literal_brackets(node.value)
    if isinstance(node, Emphasis):
        content = "".join(_compile_inline(child) for child in node.content)
        return f"**{content}**"
    if isinstance(node, Pause):
        return _PAUSE_TAGS[node.length]
    if isinstance(node, SayAs):
        return _escape_literal_brackets(node.spoken)
    if isinstance(node, Cue):
        return _CUE_TAGS[node.name]
    raise TypeError(f"Unsupported ABM node: {type(node).__name__}")


def _escape_literal_brackets(value: str) -> str:
    """Keep transcript brackets distinct from generated Gemini audio tags."""

    return value.translate(_LITERAL_BRACKET_TRANSLATION)
