# Evaluation corpus

This corpus contains original Russian text written for repeatable TTS quality
testing. It is not extracted from published books and has no FB2 preprocessing
requirements.

The corpus is organized into three groups:

- `short` contains focused samples for pronunciation, prosody, dialogue,
  punctuation, numbers, and Audiobook Markdown controls.
- `long` contains sustained literary and nonfiction narration samples for
  testing voice consistency and listening fatigue.
- `continuity` contains two consecutive parts of one scene. Generate them
  independently and listen across the boundary to assess changes in pace,
  energy, timbre, and room tone.

`manifest.json` is the machine-readable index. Every entry has a stable ID,
relative UTF-8 file path, title, and list of evaluation focuses. Text files use
the `.abm` extension and the Audiobook Markdown v0 syntax documented in the
project README.

The primary corpus intentionally keeps every individual file below the current
Eleven v3 request limit. Do not edit a benchmark passage after generating only
some model outputs; create a new corpus version so all candidates receive the
same source text.
