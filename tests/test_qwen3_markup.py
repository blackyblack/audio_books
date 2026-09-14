from __future__ import annotations

import unittest

from audiobook_tts.markup import parse
from audiobook_tts.providers.qwen3.markup import compile_document


class Qwen3MarkupTests(unittest.TestCase):
    def test_compiles_plain_transcript_for_voice_design(self) -> None:
        document = parse(
            "# Глава\n"
            "Это **важно**. {{pause:long}}{{say:МГУ|эм-гэ-у}}. "
            "{{cue:whispers}}Тише."
        )

        self.assertEqual(
            compile_document(document), "Глава\n\nЭто важно. … … эм-гэ-у. Тише."
        )


if __name__ == "__main__":
    unittest.main()
