from __future__ import annotations

import unittest

from audiobook_tts.markup import SUPPORTED_CUES, parse
from audiobook_tts.providers.google.markup import compile_document


class GoogleMarkupTests(unittest.TestCase):
    def test_compiles_document_to_gemini_prompt(self) -> None:
        document = parse(
            "# Глава первая\n"
            "Вдали показался **за́мок**. {{pause:medium}} "
            "Это {{say:МГУ|эм-гэ-у}}."
        )

        compiled = compile_document(document)

        self.assertIn("TRANSCRIPT:\nГлава первая\n\n", compiled)
        self.assertTrue(
            compiled.endswith(
                "Вдали показался **за́мок**. [pause] Это эм-гэ-у."
            )
        )

    def test_compiles_narrative_cues_to_gemini_audio_tags(self) -> None:
        document = parse(
            "{{cue:whispers}}Come closer. {{cue:sighs}} "
            "{{cue:very-slow}}There is no hurry."
        )

        compiled = compile_document(document)

        self.assertIn(
            "TRANSCRIPT:\n[whispers]Come closer. [sighs] "
            "[very slow]There is no hurry.",
            compiled,
        )
        self.assertIn(
            "Treat all bracketed text as performance directions", compiled
        )

    def test_compiles_every_supported_cue(self) -> None:
        for cue in SUPPORTED_CUES:
            with self.subTest(cue=cue):
                compiled = compile_document(parse(f"{{{{cue:{cue}}}}}Text"))
                expected_tag = f"[{cue.replace('-', ' ')}]"
                self.assertTrue(compiled.endswith(f"{expected_tag}Text"))


if __name__ == "__main__":
    unittest.main()
