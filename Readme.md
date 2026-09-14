# Russian audiobook TTS benchmark

A small command-line application for generating Russian audiobook samples.

## Requirements

- Python 3.11 or newer
- Provider credentials for the model you want to run

## Installation

Create a virtual environment and install the project:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Configure the selected provider using `.env`. Provider instructions are in its
directory under `audiobook_tts/providers`.

Supported models:

- `eleven_v3`
- `gemini-2.5-flash-preview-tts`
- `gemini-2.5-pro-preview-tts`
- `gemini-3.1-flash-tts-preview`
- `yandex-speechkit-v3`

## Usage

Generate from text supplied on the command line:

```powershell
audiobook-tts --model MODEL_ID --text "Унылая пора! Очей очарованье!"
```

For longer passages, use a UTF-8 text file:

```powershell
audiobook-tts --model MODEL_ID --input-file excerpt.md
```

The default output is `output.wav` for Gemini models and `output.mp3` for the
other providers. Use `--output` to choose another path with the model's format.

The module form works without the installed command wrapper:

```powershell
python -m audiobook_tts --model MODEL_ID --text "Пример текста."
```

## Audiobook Markdown v0

The supported subset is intentionally small:

```markdown
# Глава первая

Вдали показался **за́мок**. {{pause:medium}}

Это принадлежит {{say:МГУ|эм-гэ-у}}.
```

- `# Заголовок` — spoken heading and paragraph boundary.
- A blank line — paragraph boundary.
- `**текст**` — emphasized text.
- `за́мок` — explicit Russian stress using a Unicode acute accent.
- `{{pause:short}}` — a `short`, `medium`, or `long` pause.
- `{{say:МГУ|эм-гэ-у}}` — display/source form followed by the spoken form.

Narrative performance cues use `{{cue:name}}`. For example:

```markdown
{{cue:whispers}}Подойди ближе. {{cue:sighs}} Я надеялся, что ты поймёшь.
{{cue:serious}}Теперь слушай. {{cue:very-slow}}Спешить некуда.
```

The curated cue names are:

- Delivery: `bored`, `curious`, `excited`, `excitedly`, `mischievously`,
  `reluctantly`, `sarcastic`, `serious`, `tired`, `very-fast`, `very-slow`.
- Intense delivery: `amazed`, `crying`, `panicked`, `shouting`, `trembling`,
  `whispers`.
- Non-verbal performance: `gasp`, `giggles`, `laughs`, `sighs`.

These map to the documented Gemini audio tags and are intended primarily for
Gemini 2.5 Pro TTS and Gemini 3.1 Flash TTS. Eleven v3 receives equivalent
bracketed cues on a best-effort basis. Yandex SpeechKit has no portable inline
equivalent, so its renderer omits cues rather than speaking them. Cues influence
the passage that follows them; synthesis remains probabilistic, so use them
sparingly and audition important passages.

Unknown or malformed directives are rejected before generation.

## Evaluation corpus

Generate the complete corpus:

```powershell
audiobook-tts-corpus --model MODEL_ID
```

Existing outputs are skipped by default. Pass `--overwrite` only when you
intend to regenerate them. The same runner is available with:

```powershell
python scripts/run_corpus.py --model MODEL_ID
```

See `corpus/README.md` for corpus-specific information.

## Tests

```powershell
python -m unittest discover -s tests -v
```
