from __future__ import annotations

import unittest

from audiobook_tts.markup import parse
from audiobook_tts.providers.chirp3.markup import compile_document


class Chirp3MarkupTests(unittest.TestCase):
    def test_compiles_supported_abm_to_ssml(self) -> None:
        document = parse(
            "# Глава & первая\n"
            "Там был **замок**. {{pause:medium}} "
            "Это {{say:МГУ|эм-гэ-у}}. {{cue:whispers}}Тише."
        )

        self.assertEqual(
            compile_document(document),
            "<speak><p>Глава &amp; первая</p>"
            '<p>Там был <prosody volume="loud">замок</prosody>. '
            '<break time="400ms"/> Это <sub alias="эм-гэ-у">МГУ</sub>. Тише.</p>'
            "</speak>",
        )

if __name__ == "__main__":
    unittest.main()
