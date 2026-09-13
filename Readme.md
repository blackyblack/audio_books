# Russian audiobook TTS benchmark

A small command-line application for generating Russian audiobook samples. The
first integrated provider is ElevenLabs, using the `eleven_v3` model.

This is an evaluation tool, not a production audiobook pipeline. It accepts
already-prepared text, compiles a small provider-independent Audiobook Markdown
(ABM) subset, and writes the generated audio to a local MP3 file.

## Requirements

- Python 3.11 or newer
- An ElevenLabs account and API key

## Installation

Create a virtual environment and install the project:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## ElevenLabs credentials

1. Create or sign in to an account at <https://elevenlabs.io/>.
2. Open **Developers**, then **API Keys**, and create a key. Give it Text to
   Speech permission; setting a small credit limit is recommended for this
   benchmark. The official instructions are at
   <https://elevenlabs.io/docs/help-center/technical/how-do-i-authorize-myself-using-an-api-key>.
3. Optional: select a Russian-capable voice in the Voice Library or your own
   Voices page and copy its voice ID. The API also exposes a list-voices endpoint:
   <https://elevenlabs.io/docs/api-reference/voices/search>.
4. Put both values in the local `.env` file:

```dotenv
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=
```

When `ELEVENLABS_VOICE_ID` is empty, the CLI uses ElevenLabs' documented
**George** sample voice (`JBFqnCBsd6RMkjVDRZzb`). Set a voice ID explicitly
when evaluating voices chosen for Russian narration.

The application loads `.env` from the current working directory on every
start. `.env` is ignored by Git; `.env.example` documents the required names.

## Usage

Generate from text supplied on the command line:

```powershell
audiobook-tts --model eleven_v3 --text "Унылая пора! Очей очарованье!" --output sample.mp3
```

For longer passages, use a UTF-8 text file:

```powershell
audiobook-tts --model eleven_v3 --input-file excerpt.md --output sample.mp3
```

The module form works without the installed command wrapper:

```powershell
python -m audiobook_tts --model eleven_v3 --text "Пример текста."
```

Use `--voice-id` to override `ELEVENLABS_VOICE_ID` for one generation.

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

ABM is compiled to Eleven v3 audio cues. Stress marks are retained. `say`
directives synthesize only the spoken form. Unknown or malformed ABM directives
fail before making a billable API call.

Eleven v3 accepts at most 5,000 compiled characters per request. This initial
CLI reports an error for longer input rather than silently splitting it, so a
quality evaluation cannot accidentally include stitching artifacts.

## Tests

```powershell
python -m unittest discover -s tests -v
```
