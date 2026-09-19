# Google Cloud Chirp 3 HD provider

Supported model: `chirp3-hd`.

## Obtain credentials

1. [Create or select a Google Cloud project, link a billing account, and enable
   the Cloud Text-to-Speech API](https://cloud.google.com/text-to-speech/docs/get-started).
2. In Google Cloud Console, open **IAM & Admin > Service Accounts** and create a
   service account for this application. Grant only the minimum project access
   required by your organization's policy; do not use Owner or Editor merely
   for text-to-speech access.
3. Open the service account, select **Keys > Add key > Create new key**, choose
   **JSON**, and download the key. Google only lets you download that private
   key once. See Google's [service-account key
   instructions](https://cloud.google.com/iam/docs/keys-create-delete).
4. Store the downloaded file outside source control. For this repository, it
   can be renamed to `chirp3.json` in the project root; that filename is ignored
   by Git. Never commit, share, or paste the file into logs. Disable/delete the
   key and create a replacement immediately if it is exposed.
5. Add the credential path and, optionally, a Russian voice to `.env`:

```dotenv
GOOGLE_APPLICATION_CREDENTIALS=chirp3.json
CHIRP3_VOICE=
```

The path may be absolute if the JSON file is stored elsewhere. The default
voice is `ru-RU-Chirp3-HD-Kore`; `--voice-id` overrides it.

For local development, a safer alternative to a long-lived JSON key is
[Application Default Credentials](https://cloud.google.com/text-to-speech/docs/authentication):

```powershell
gcloud init
gcloud auth application-default login
```

When using this method, leave `GOOGLE_APPLICATION_CREDENTIALS` unset.

## Evaluation status

Chirp 3 officially supports Russian voices, but Russian generation in this
benchmark is below expectations. Keep this provider as a comparative option
rather than assuming it meets production audiobook quality without listening
tests on the intended material and voice.

## Commands

```powershell
audiobook-tts --model chirp3-hd --input-file excerpt.md
audiobook-tts-corpus --model chirp3-hd
```

Audio is written as MP3. Paragraphs, pauses, spoken substitutions, and emphasis
are rendered with Chirp 3 HD SSML. Emotional performance cues are omitted
because Chirp has no equivalent inline emotional-direction syntax. Narrator
style is ignored with a console warning.
