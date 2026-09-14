from __future__ import annotations

import unittest

from audiobook_tts.markup import (
    Document,
    Emphasis,
    Heading,
    MarkupError,
    Paragraph,
    Pause,
    SayAs,
    Text,
    parse,
)


class MarkupTests(unittest.TestCase):
    def test_parses_supported_abm_without_provider_details(self) -> None:
        source = (
            "# Глава первая\n\n"
            "Вдали показался **за́мок**. {{pause:medium}}\n"
            "Это {{say:МГУ|эм-гэ-у}}."
        )

        document = parse(source)

        self.assertEqual(
            document,
            Document(
                blocks=(
                    Heading(level=1, content=(Text("Глава первая"),)),
                    Paragraph(
                        content=(
                            Text("Вдали показался "),
                            Emphasis("за́мок"),
                            Text(". "),
                            Pause("medium"),
                            Text("\nЭто "),
                            SayAs(display="МГУ", spoken="эм-гэ-у"),
                            Text("."),
                        )
                    ),
                )
            ),
        )

    def test_rejects_unknown_directive(self) -> None:
        with self.assertRaisesRegex(MarkupError, "Unknown or malformed"):
            parse("Текст {{emotion:sad}}")

    def test_rejects_unclosed_emphasis(self) -> None:
        with self.assertRaisesRegex(MarkupError, "malformed emphasis"):
            parse("Это **важно.")

    def test_rejects_empty_input(self) -> None:
        with self.assertRaisesRegex(MarkupError, "must not be empty"):
            parse("  \n")


if __name__ == "__main__":
    unittest.main()
