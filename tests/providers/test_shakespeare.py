# pylint: disable=no-self-use,missing-docstring, too-few-public-methods

import json

import pytest
import requests as rr
import responses

from pokepi.providers.common import ProviderError, ValidationError, validate
from pokepi.providers.shakespeare import (
    URL,
    VALIDATION_SCHEMA,
    extract,
    get_translation,
    shakespeare_processor,
)


class TestGetTranslation:
    def test_ok(self, retrying_response):
        text = "This is a test text."
        expected = {
            "success": {"total": 1},
            "contents": {
                "translated": "translated_text",
                "text": text,
                "translation": "shakespeare",
            },
        }

        retrying_response.add(
            responses.POST,
            URL,
            body=json.dumps(expected),
            content_type="application/json",
            status=200,
        )

        assert get_translation(text) == expected

    def test_http_error(self, retrying_response):
        text = "This is a test text."

        retrying_response.add(
            responses.POST,
            URL,
            body="Internal Server Error",
            content_type="text/plan",
            status=500,
        )

        with pytest.raises(
            ProviderError, match="Unexpected error from Shakespeare API"
        ):
            get_translation(text)

    def test_unexpected_error(self, retrying_response):
        text = "This is a test text."

        retrying_response.add(
            responses.POST,
            URL,
            body=rr.ConnectionError("Connection error"),
        )

        with pytest.raises(
            ProviderError, match="Unexpected error from Shakespeare API"
        ):
            get_translation(text)


class TestValidate:
    def test_valid_data(self):
        data = {
            "success": {"total": 1},
            "contents": {
                "translated": "translated text",
                "text": "original text",
                "translation": "shakespeare",
            },
        }
        expexted = {
            "contents": {
                "translated": "translated text",
                "text": "original text",
                "translation": "shakespeare",
            },
        }

        assert validate(data, VALIDATION_SCHEMA) == expexted

    def test_invalid_data(self):
        invalid_data = {"invalid": 10}

        with pytest.raises(ValidationError):
            validate(invalid_data, VALIDATION_SCHEMA)


class TestExtract:
    def test_text(self):
        payload = {
            "success": {"total": 1},
            "contents": {
                "translated": "translated_text",
                "text": "original_text",
                "translation": "shakespeare",
            },
        }

        assert extract(payload) == "translated_text"


class TestShakespeareProcessor:
    def test_ok(self, retrying_response):
        text = "This is a test text."
        response_data = {
            "success": {"total": 1},
            "contents": {
                "translated": "translated_text",
                "text": text,
                "translation": "shakespeare",
            },
        }

        retrying_response.add(
            responses.POST,
            URL,
            body=json.dumps(response_data),
            content_type="application/json",
            status=200,
        )

        assert shakespeare_processor(text) == "translated_text"

    def test_io_error(self, retrying_response):
        text = "This is a test text."

        retrying_response.add(
            responses.POST,
            URL,
            body=rr.ConnectionError("Connection error"),
        )

        with pytest.raises(
            ProviderError, match="Unexpected error from Shakespeare API"
        ):
            shakespeare_processor(text)

    def test_validation_error(self, retrying_response):
        text = "This is a test text."
        response_data = {
            "success": {"total": 1},
            "contents": {},
        }

        retrying_response.add(
            responses.POST,
            URL,
            body=json.dumps(response_data),
            content_type="application/json",
            status=200,
        )

        with pytest.raises(ValidationError):
            shakespeare_processor(text)
