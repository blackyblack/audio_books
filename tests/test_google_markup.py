from __future__ import annotations

import unittest

from audiobook_tts.markup import DEFAULT_NARRATOR_STYLE, SUPPORTED_CUES, parse
from audiobook_tts.providers.google.markup import compile_document


class GoogleMarkupTests(unittest.TestCase):
    def test_compiles_document_to_gemini_prompt(self) -> None:
        document = parse(
            "# Глава первая\n"
            "Вдали показался **за́мок**. {{pause:medium}} "
            "Это {{say:МГУ|эм-гэ-у}}."
        )

        compiled = compile_document(document)

        self.assertIn(f"NARRATOR STYLE:\n{DEFAULT_NARRATOR_STYLE}", compiled)
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
            "single square-bracketed controls as performance directions", compiled
        )

    def test_compiles_every_supported_cue(self) -> None:
        for cue in SUPPORTED_CUES:
            with self.subTest(cue=cue):
                compiled = compile_document(parse(f"{{{{cue:{cue}}}}}Text"))
                expected_tag = f"[{cue.replace('-', ' ')}]"
                self.assertTrue(compiled.endswith(f"{expected_tag}Text"))

    def test_preserves_literal_square_bracket_content(self) -> None:
        document = parse("Он выбрал диапазон [а, б]. {{cue:whispers}}Тише.")

        compiled = compile_document(document)

        self.assertTrue(
            compiled.endswith("Он выбрал диапазон [[а, б]]. [whispers]Тише.")
        )
        self.assertIn(
            "Doubled square brackets are literal transcript punctuation; "
            "speak their contents normally.",
            compiled,
        )

    def test_preserves_literal_brackets_in_say_as_spoken_form(self) -> None:
        document = parse("Термин {{say:API|эй-пи-ай [устаревшее]}}.")

        compiled = compile_document(document)

        self.assertTrue(compiled.endswith("Термин эй-пи-ай [[устаревшее]]."))

    def test_compiles_narrator_style(self) -> None:
        document = parse(
            "{{narrator-style:Measured and atmospheric.}}\n\nОна вошла."
        )

        compiled = compile_document(document)

        self.assertIn("NARRATOR STYLE:\nMeasured and atmospheric.", compiled)
        self.assertNotIn(DEFAULT_NARRATOR_STYLE, compiled)
        self.assertTrue(compiled.endswith("TRANSCRIPT:\nОна вошла."))


if __name__ == "__main__":
    unittest.main()
