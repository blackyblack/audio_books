# Google Gemini provider

Supported models:

- `gemini-2.5-flash-preview-tts`
- `gemini-2.5-pro-preview-tts`

## Credentials

1. Create an API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Set the provider values in the repository's `.env` file:

```dotenv
GOOGLE_API_KEY=your_key_here
GOOGLE_VOICE=
```

`GOOGLE_API_KEY` is required. When `GOOGLE_VOICE` is empty, the provider uses
`Kore`. Available voices are listed in the
[Gemini TTS guide](https://ai.google.dev/gemini-api/docs/speech-generation#voices).

## Commands

Generate one sample:

```powershell
audiobook-tts --model gemini-2.5-flash-preview-tts --input-file excerpt.md
```

Generate the entire corpus:

```powershell
audiobook-tts-corpus --model gemini-2.5-flash-preview-tts
```

Flash audio is written as WAV; Pro audio is written as MP3. Corpus output is
placed beneath `outputs/<model>`.
