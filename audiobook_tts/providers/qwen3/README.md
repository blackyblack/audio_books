# Qwen3 TTS Voice Design provider

Supported model: `qwen3-tts-vd-2026-01-26`.

## Evaluation status

The faster instruction-control model `qwen3-tts-instruct-flash` was tested
previously. Its Russian audiobook output was below expectations. The current
Voice Design model, `qwen3-tts-vd-2026-01-26`, is also below expectations, so
the model change should not be interpreted as a quality recommendation.

Voice cloning may produce better results when given a clean, expressive Russian
reference recording. The most promising Qwen path to evaluate next is a cloned
voice with a model that supports Russian, such as `qwen-audio-3.0-tts-plus` or
`qwen3-tts-vc-2026-01-22`. Results are not guaranteed, and the recording must be
used with the speaker's authorization. See Alibaba Cloud's [voice-cloning
guide](https://www.alibabacloud.com/help/en/model-studio/voice-cloning-user-guide).

## Why Voice Design

`qwen3-tts-vd-2026-01-26` does not accept Qwen system voices such as `Cherry`.
It requires a voice ID created for that exact model by the Voice Design API.
The provider creates an audiobook-oriented Russian voice on its first run and
caches the returned ID for later runs.

Alibaba's newer quality-first `qwen-audio-3.0-tts-plus` model requires a cloned
voice to synthesize Russian; its documented ready-made system voices cover
Chinese and English. It is therefore not a drop-in provider for this Russian
benchmark without an authorized Russian reference recording. See Alibaba's
[TTS model overview](https://www.alibabacloud.com/help/en/model-studio/tts-model/)
for the current language and voice-mode matrix.

## Configuration

Create an Alibaba Cloud Model Studio API key for the Singapore region and add:

```dotenv
DASHSCOPE_API_KEY=your_key_here
QWEN_VOICE=
QWEN_BASE_URL=
QWEN_VOICE_PROMPT=
QWEN_VOICE_CACHE=
```

The default endpoint is the Singapore (`dashscope-intl`) endpoint. The first
run creates a designed voice and stores its ID in `.qwen3-tts-vd-voice`.
Alibaba currently charges for Qwen voice creation; synthesis is billed
separately. Subsequent runs reuse the cached ID and do not create another
voice.

Set `QWEN_VOICE_PROMPT` to customize the English voice description before the
first run. Set `QWEN_VOICE` (or pass `--voice-id`) to use an existing voice ID
created specifically for `qwen3-tts-vd-2026-01-26`; this skips voice creation.
`QWEN_VOICE_CACHE` can override the cache path.

```powershell
audiobook-tts --model qwen3-tts-vd-2026-01-26 --input-file excerpt.md
audiobook-tts-corpus --model qwen3-tts-vd-2026-01-26
```

Audio is written as WAV. Inputs longer than Qwen's 600-character request limit
are split at natural text boundaries and the returned PCM WAV segments are
joined. ABM pauses become punctuation-based pauses and spoken substitutions are
preserved. Voice Design has no instruction-control or position-scoped cue API,
so performance cues are omitted.
