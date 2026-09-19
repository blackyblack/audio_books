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
`Kore`.

## Voices

`--voice-id` and `GOOGLE_VOICE` accept a case-sensitive Gemini prebuilt voice
name. They do not accept an arbitrary or custom name.

Supported voice names:

- `Zephyr` — Bright
- `Puck` — Upbeat
- `Charon` — Informative
- `Kore` — Firm
- `Fenrir` — Excitable
- `Leda` — Youthful
- `Orus` — Firm
- `Aoede` — Breezy
- `Callirrhoe` — Easy-going
- `Autonoe` — Bright
- `Enceladus` — Breathy
- `Iapetus` — Clear
- `Umbriel` — Easy-going
- `Algieba` — Smooth
- `Despina` — Smooth
- `Erinome` — Clear
- `Algenib` — Gravelly
- `Rasalgethi` — Informative
- `Laomedeia` — Upbeat
- `Achernar` — Soft
- `Alnilam` — Firm
- `Schedar` — Even
- `Gacrux` — Mature
- `Pulcherrima` — Forward
- `Achird` — Friendly
- `Zubenelgenubi` — Casual
- `Vindemiatrix` — Gentle
- `Sadachbia` — Lively
- `Sadaltager` — Knowledgeable
- `Sulafat` — Warm

Select the voice with:

```powershell
audiobook-tts --model gemini-3.1-flash-tts-preview --voice-id Kore --input-file excerpt.md
```

Gemini supports Russian. See Google's
[Gemini TTS guide](https://ai.google.dev/gemini-api/docs/speech-generation#voices)
for voice previews and current platform details.

## Commands

```powershell
audiobook-tts --model gemini-3.1-flash-tts-preview --input-file excerpt.md
audiobook-tts-corpus --model gemini-3.1-flash-tts-preview
```

## Provider behavior

Audio is written as WAV. Performance cues compile to Gemini audio tags;
narrator style is sent as a natural-language direction. Literal square brackets
are escaped before generation. When ABM does not specify a narrator style, the
default is clear, neutral narration with natural pacing and restrained
expression.
