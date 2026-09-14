from __future__ import annotations

import unittest

from audiobook_tts.markup import parse
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


if __name__ == "__main__":
    unittest.main()
