# pylint: disable=no-self-use,missing-docstring

import json

import pytest
import requests as rr
import responses

from pokepi.providers.shakespeare import URL, TranslationError, get_translation


@pytest.fixture(name="retrying_response")
def fixture_retrying_response():
    with responses.RequestsMock(
        target="pokepi.providers.common.HTTPAdapterWithDefaultTimeout.send"
    ) as m_resp:
        yield m_resp


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

        with pytest.raises(TranslationError):
            get_translation(text)

    def test_unexpected_error(self, retrying_response):
        text = "This is a test text."

        retrying_response.add(
            responses.POST,
            URL,
            body=rr.ConnectionError("Connection error"),
        )

        with pytest.raises(TranslationError):
            get_translation(text)
