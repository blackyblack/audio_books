from __future__ import annotations

import unittest

from audiobook_tts.markup import MarkupError, compile_for_elevenlabs


class MarkupTests(unittest.TestCase):
    def test_compiles_supported_abm(self) -> None:
        source = (
            "# Глава первая\n\n"
            "Вдали показался **за́мок**. {{pause:medium}}\n"
            "Это {{say:МГУ|эм-гэ-у}}."
        )

        compiled = compile_for_elevenlabs(source)

        self.assertEqual(
            compiled,
            "Глава первая\n\n"
            "Вдали показался ЗА́МОК. [pause]\n"
            "Это эм-гэ-у.",
        )

    def test_rejects_unknown_directive(self) -> None:
        with self.assertRaisesRegex(MarkupError, "Unknown or malformed"):
            compile_for_elevenlabs("Текст {{emotion:sad}}")

    def test_rejects_unclosed_emphasis(self) -> None:
        with self.assertRaisesRegex(MarkupError, "Unclosed emphasis"):
            compile_for_elevenlabs("Это **важно.")

    def test_rejects_empty_input(self) -> None:
        with self.assertRaisesRegex(MarkupError, "must not be empty"):
            compile_for_elevenlabs("  \n")


if __name__ == "__main__":
    unittest.main()
