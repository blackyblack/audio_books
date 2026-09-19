# Audiobook Markdown (ABM)

Audiobook Markdown is a portable text format for audiobook synthesis. It keeps
the readable book text while adding pronunciation, performance, narrator-style,
and structural information.

Unknown or malformed directives make the document invalid.

## Complete example

```markdown
{{narrator-style:Literary, atmospheric narration with measured pacing and restrained emotion.}}

# Глава первая

Анна вошла и остановилась. {{pause:short}}

{{cue:whispers}}— Я не ждала вас.
{{cue:serious}}— Нам нужно поговорить.

Она произнесла {{say:МГУ|эм-гэ-у}} особенно отчётливо.
```

## Preamble

The optional preamble must come before headings or spoken text. Blank lines may
separate its directives.

- `{{narrator-style:description}}` sets the overall narrator delivery, tone,
  pacing, and emotional range. A document may contain at most one. When it is
  omitted, the style is `Clear and neutral audiobook narration with natural
  pacing and restrained expression.`

## Spoken structure and inline directives

- `# Heading` through `###### Heading` are spoken headings and block
  boundaries.
- A blank line creates a paragraph boundary.
- `**text**` requests emphasis.
- A Unicode combining acute accent sets explicit Russian stress: `за́мок`.
- `{{pause:short}}`, `{{pause:medium}}`, and `{{pause:long}}` request pauses.
- `{{say:display|spoken}}` preserves a source form while supplying the spoken
  form, for example `{{say:МГУ|эм-гэ-у}}`.
- `{{cue:name}}` changes the performance of the following text.

Supported cue names:

- Delivery: `bored`, `curious`, `excited`, `excitedly`, `mischievously`,
  `reluctantly`, `sarcastic`, `serious`, `tired`, `very-fast`, `very-slow`.
- Intense delivery: `amazed`, `crying`, `panicked`, `shouting`, `trembling`,
  `whispers`.
- Non-verbal performance: `gasp`, `giggles`, `laughs`, `sighs`.

Cues express performance intent rather than literal spoken text. Ordinary
square brackets are literal book text, not ABM controls.
