from __future__ import annotations

import unittest

from audiobook_tts.markup import (
    Cue,
    Document,
    Emphasis,
    Heading,
    MarkupError,
    Paragraph,
    Pause,
    SayAs,
    SUPPORTED_CUES,
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
                            Emphasis(content=(Text("за́мок"),)),
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

    def test_parses_documented_narrative_cue(self) -> None:
        document = parse("{{cue:whispers}}Quietly.")

        self.assertEqual(
            document,
            Document(
                blocks=(
                    Paragraph(content=(Cue("whispers"), Text("Quietly."))),
                )
            ),
        )

    def test_every_supported_cue_parses(self) -> None:
        for cue in SUPPORTED_CUES:
            with self.subTest(cue=cue):
                document = parse(f"{{{{cue:{cue}}}}}Text")
                self.assertEqual(
                    document.blocks[0],
                    Paragraph(content=(Cue(cue), Text("Text"))),
                )

    def test_rejects_undocumented_cue(self) -> None:
        with self.assertRaisesRegex(MarkupError, "Unsupported ABM cue 'happy'"):
            parse("{{cue:happy}}Text")

    def test_heading_does_not_require_a_blank_line_before_body(self) -> None:
        document = parse("# Глава\nТекст")

        self.assertEqual(
            document,
            Document(
                blocks=(
                    Heading(level=1, content=(Text("Глава"),)),
                    Paragraph(content=(Text("Текст"),)),
                )
            ),
        )

    def test_rejects_unknown_directive_inside_emphasis(self) -> None:
        with self.assertRaisesRegex(MarkupError, "Unknown or malformed"):
            parse("**текст {{emotion:sad}}**")

    def test_parses_supported_directive_inside_emphasis(self) -> None:
        document = parse("**текст {{pause:short}}**")

        self.assertEqual(
            document,
            Document(
                blocks=(
                    Paragraph(
                        content=(
                            Emphasis(content=(Text("текст "), Pause("short"))),
                        )
                    ),
                )
            ),
        )

    def test_rejects_unclosed_emphasis(self) -> None:
        with self.assertRaisesRegex(MarkupError, "malformed emphasis"):
            parse("Это **важно.")

    def test_rejects_empty_input(self) -> None:
        with self.assertRaisesRegex(MarkupError, "must not be empty"):
            parse("  \n")


if __name__ == "__main__":
    unittest.main()
