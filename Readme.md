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

Configure the selected provider using `.env`:

- [ElevenLabs](audiobook_tts/providers/eleven_labs/README.md)
- [Google Cloud Chirp 3 HD](audiobook_tts/providers/chirp3/README.md)
- [Google](audiobook_tts/providers/google/README.md)
- [Qwen3 TTS Voice Design](audiobook_tts/providers/qwen3/README.md)
- [Yandex](audiobook_tts/providers/yandex/README.md)

Each provider guide lists its supported models, credentials, voices, output
format, and provider-specific behavior.

## Supported model IDs

Pass one of these exact values to `--model`:

- ElevenLabs: `eleven_v3`
- Google Cloud Text-to-Speech: `chirp3-hd`
- Google Gemini TTS: `gemini-2.5-flash-preview-tts`
- Google Gemini TTS: `gemini-2.5-pro-preview-tts`
- Google Gemini TTS: `gemini-3.1-flash-tts-preview`
- Qwen3 TTS Voice Design: `qwen3-tts-vd-2026-01-26`
- Yandex SpeechKit: `yandex-speechkit-v3`

The same list is shown by `audiobook-tts --help` and
`audiobook-tts-corpus --help`. Values such as provider display names or voice
IDs are not valid `--model` arguments.

## Usage

Generate from text supplied on the command line:

```powershell
audiobook-tts --model MODEL_ID --text "Унылая пора! Очей очарованье!"
```

For longer passages, use a UTF-8 text file:

```powershell
audiobook-tts --model MODEL_ID --input-file excerpt.md
```

The default filename is `output` with the selected provider's file extension.
Use `--output` to choose another path with that same extension.
Use `--voice-id VOICE_ID` to override the single configured voice; provider
guides list accepted voice values.

The module form works without the installed command wrapper:

```powershell
python -m audiobook_tts --model MODEL_ID --text "Пример текста."
```

## Audiobook Markdown

ABM defines headings, emphasis, stress, pauses, spoken substitutions,
performance cues, and narrator-style direction. See [ABM.md](ABM.md) for the
complete syntax.

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
