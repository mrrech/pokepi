# pylint: disable=no-self-use,missing-docstring

from pokepi.providers.pokeapi import sanitize


class TestSanitize:
    def test_whitespaces(self):
        text = "into\x0can almost perfect\ncopy of its oppo\xad\nnent."
        expected_text = "into an almost perfect copy of its opponent."

        assert sanitize(text) == expected_text

    def test_hyphens(self):
        text = "cellular\nstructure to trans\xad\nform into other life-\nforms."
        expected_text = "cellular structure to transform into other life-forms."

        assert sanitize(text) == expected_text

    def test_empty_string(self):
        text = ""
        expected_text = ""

        assert sanitize(text) == expected_text
