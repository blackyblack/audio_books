from __future__ import annotations

import unittest

from audiobook_tts.markup import parse
from audiobook_tts.providers.yandex.markup import compile_document


class YandexMarkupTests(unittest.TestCase):
    def test_compiles_document_to_speechkit_markup(self) -> None:
        document = parse(
            "# Глава первая\n"
            "Вдали показался **за́мок**. {{pause:medium}} "
            "Это {{say:МГУ|эм-гэ-у}}."
        )

        compiled = compile_document(document)

        self.assertEqual(
            compiled,
            "Глава первая\n\n"
            "Вдали показался **з+амок**. sil<[400]> Это эм-гэ-у.",
        )


if __name__ == "__main__":
    unittest.main()
