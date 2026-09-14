# ElevenLabs provider

Supported model: `eleven_v3`.

## Credentials

1. Create or sign in to an account at <https://elevenlabs.io/>.
2. Open **Developers**, then **API Keys**, and create a key with Text to Speech
   permission. See the official authentication guide at
   <https://elevenlabs.io/docs/help-center/technical/how-do-i-authorize-myself-using-an-api-key>.
3. Optional: select a voice in the Voice Library or your Voices page and copy
   its voice ID. The list-voices endpoint is documented at
   <https://elevenlabs.io/docs/api-reference/voices/search>.
4. Set the provider values in the repository's `.env` file:

```dotenv
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=
```

`ELEVENLABS_API_KEY` is required. When `ELEVENLABS_VOICE_ID` is empty, the
provider uses the George sample voice, `JBFqnCBsd6RMkjVDRZzb`.

Input is limited to 5,000 generated characters per request. Longer input is
rejected rather than split automatically.

## Commands

Generate one sample:

```powershell
audiobook-tts --model eleven_v3 --input-file corpus/short/07_stress_homographs.abm --output stress.mp3
```

Generate the entire corpus:

```powershell
audiobook-tts-corpus --model eleven_v3
```

Corpus audio is written beneath `outputs/eleven_v3`. Existing files are skipped
unless `--overwrite` is provided.
