# pylint: disable=no-self-use,missing-docstring

import json

import pytest

from pokepi.providers.pokeapi import ValidationError, sanitize, validate


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


class TestValidate:
    def test_valid_data(self, datadir):
        data = json.loads((datadir / "ditto.json").read_text())
        expexted = json.loads((datadir / "validated_ditto.json").read_text())

        assert validate(data) == expexted

    def test_invalid_data(self):
        invalid_data = {"invalid": 10}

        with pytest.raises(ValidationError):
            validate(invalid_data)
