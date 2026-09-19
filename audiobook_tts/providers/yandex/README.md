# Yandex SpeechKit provider

Supported model: `yandex-speechkit-v3`.

## Credentials

1. Create a Yandex Cloud service account.
2. Grant it the `ai.speechkit-tts.user` role.
3. Create an API key for the service account by following the
   [Yandex API key guide](https://yandex.cloud/en/docs/iam/operations/authentication/manage-api-keys#create-api-key).
4. Set the provider values in the repository's `.env` file:

```dotenv
YANDEX_API_KEY=your_key_here
YANDEX_VOICE=
```

`YANDEX_API_KEY` is required. When `YANDEX_VOICE` is empty, the provider uses
`marina`. Other Russian voices are listed in the
[SpeechKit voice guide](https://yandex.cloud/en/docs/speechkit/tts/voices).

## Commands

Generate one sample:

```powershell
audiobook-tts --model yandex-speechkit-v3 --input-file excerpt.md
```

Generate the entire corpus:

```powershell
audiobook-tts-corpus --model yandex-speechkit-v3
```

Yandex audio is written as MP3. Corpus output is placed beneath
`outputs/yandex-speechkit-v3`.

SpeechKit markup has no portable inline equivalent for Audiobook Markdown
performance cues. The renderer omits cue directions rather than speaking them;
the surrounding transcript is preserved. Narrator style is ignored with a
console warning.
