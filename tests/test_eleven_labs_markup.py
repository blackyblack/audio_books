from __future__ import annotations

import unittest

from audiobook_tts.markup import parse
from audiobook_tts.providers.eleven_labs.markup import compile_document


class ElevenLabsMarkupTests(unittest.TestCase):
    def test_compiles_document_to_eleven_v3_cues(self) -> None:
        document = parse(
            "# Глава первая\n\n"
            "Вдали показался **за́мок**. {{pause:medium}}\n"
            "Это {{say:МГУ|эм-гэ-у}}."
        )

        compiled = compile_document(document)

        self.assertEqual(
            compiled,
            "Глава первая\n\n"
            "Вдали показался ЗА́МОК. [pause]\n"
            "Это эм-гэ-у.",
        )

    def test_compiles_portable_narrative_cues(self) -> None:
        document = parse("{{cue:whispers}}Quiet. {{cue:very-slow}}Wait.")

        self.assertEqual(
            compile_document(document), "[whispers]Quiet. [very slow]Wait."
        )


if __name__ == "__main__":
    unittest.main()
