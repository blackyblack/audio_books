# Google Gemini provider

Supported models:

- `gemini-2.5-flash-preview-tts`
- `gemini-2.5-pro-preview-tts`
- `gemini-3.1-flash-tts-preview`

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
audiobook-tts --model gemini-3.1-flash-tts-preview --input-file excerpt.md
```

Generate the entire corpus:

```powershell
audiobook-tts-corpus --model gemini-3.1-flash-tts-preview
```

Gemini audio is written as WAV. Corpus output is placed beneath
`outputs/<model>`.

Audiobook Markdown `{{cue:name}}` directives compile to Gemini's documented
inline audio tags. The schema deliberately supports a curated narrative subset
instead of arbitrary tags so typos fail before a billable request. See the
project README for the complete cue list.

Google recommends English audio tags even when the transcript is in another
language; ABM therefore keeps cue names in English. Tags influence the following
line or section rather than marking a rigorously bounded span. Keep directions
coherent with the selected voice and split long 3.1 generations into chunks of
a few minutes to reduce voice and quality drift.

Ordinary square brackets remain literal ABM text. The renderer visibly doubles
them in the generated prompt (`[text]` becomes `[[text]]`) so Gemini can
distinguish transcript punctuation from single-bracket audio-tag directions.
