# pylint: disable=no-self-use,missing-docstring

import json

import pytest
import requests as rr
import responses

from pokepi.providers.common import (
    ProviderError,
    ResourceNotFound,
    ValidationError,
    validate,
)
from pokepi.providers.pokeapi import (
    URL,
    VALIDATION_SCHEMA,
    extract,
    get_pokemon_species,
    pokeapi_processor,
    sanitize,
)


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

        assert validate(data, VALIDATION_SCHEMA) == expexted

    def test_invalid_data(self):
        invalid_data = {"invalid": 10}

        with pytest.raises(ValidationError):
            validate(invalid_data, VALIDATION_SCHEMA)


class TestExtract:
    def test_english(self):
        data = {
            "flavor_text_entries": [
                {
                    "flavor_text": "a_text_1",
                    "language": {"name": "en", "url": "url_1"},
                },
                {
                    "flavor_text": "a_text_2",
                    "language": {"name": "en", "url": "url_2"},
                },
            ]
        }

        expected_data = ["a_text_1", "a_text_2"]

        assert extract(data) == expected_data

    def test_any_language(self):
        data = {
            "flavor_text_entries": [
                {
                    "flavor_text": "a_text_1",
                    "language": {"name": "it", "url": "url_1"},
                },
                {
                    "flavor_text": "a_text_2",
                    "language": {"name": "de", "url": "url_2"},
                },
                {
                    "flavor_text": "a_text_3",
                    "language": {"name": "en", "url": "url_3"},
                },
            ]
        }

        assert extract(data) == ["a_text_3"]


class TestGetPokemonSpecies:
    def test_ok(self, retrying_response):
        name = "ditto"

        retrying_response.add(
            responses.GET,
            URL.format(name=name),
            body="{}",
            content_type="application/json",
            status=200,
        )

        assert get_pokemon_species(name) == {}

    def test_not_found(self, retrying_response):
        name = "not-found"

        retrying_response.add(
            responses.GET,
            URL.format(name=name),
            body="Not Found",
            content_type="text/plan",
            status=404,
        )

        with pytest.raises(ResourceNotFound, match="Pokemon 'not-found' not found"):
            get_pokemon_species(name)

    def test_http_error(self, retrying_response):
        name = "ditto"

        retrying_response.add(
            responses.GET,
            URL.format(name=name),
            body="Internal Server Error",
            content_type="text/plan",
            status=500,
        )

        with pytest.raises(
            ProviderError, match="HTTP error from PokeAPI: 500, Internal Server Error"
        ):
            get_pokemon_species(name)

    def test_unexpected_error(self, retrying_response):
        name = "ditto"

        retrying_response.add(
            responses.GET,
            URL.format(name=name),
            body=rr.ConnectionError("Connection error"),
        )

        with pytest.raises(ProviderError, match="Unexpected error from PokeAPI"):
            get_pokemon_species(name)


class TestPokeapiProcessor:
    def test_ok(self, retrying_response, datadir):
        name = "ditto"
        data = (datadir / "ditto.json").read_text()
        expected_description = """\
DITTO rearranges its cell structure to transform itself into other shapes. However, if it tries to transform itself into something by relying on its memory, this POKéMON manages to get details wrong.\
"""

        retrying_response.add(
            responses.GET,
            URL.format(name=name),
            body=data,
            content_type="application/json",
            status=200,
        )

        assert pokeapi_processor(name) == expected_description

    def test_io_error(self, retrying_response):
        name = "ditto"

        retrying_response.add(
            responses.GET,
            URL.format(name=name),
            body=rr.ConnectionError("Connection error"),
        )

        with pytest.raises(ProviderError, match="Unexpected error from PokeAPI"):
            pokeapi_processor(name)

    def test_validation_error(self, retrying_response):
        name = "ditto"

        retrying_response.add(
            responses.GET,
            URL.format(name=name),
            body="{}",
            content_type="application/json",
            status=200,
        )

        with pytest.raises(ValidationError):
            pokeapi_processor(name)

    def test_unexpected_error(self, retrying_response, datadir):
        name = "ditto"
        data = (datadir / "ditto-empty-descriptions.json").read_text()

        retrying_response.add(
            responses.GET,
            URL.format(name=name),
            body=data,
            content_type="application/json",
            status=200,
        )

        with pytest.raises(IndexError, match="list index out of range"):
            pokeapi_processor(name)
