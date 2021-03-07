# pylint: disable=no-self-use,missing-docstring

import tempfile

from pathlib import Path
from unittest.mock import patch

import pytest

from pokepi.app import pokepi_application_factory
from pokepi.providers import ProviderError, ResourceNotFound


@pytest.fixture(name="test_app")
def app_fixture():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(Path(temp_dir) / "index.html", "w") as fd:
            fd.write("docs!")

        app = pokepi_application_factory(
            "test_pokepi", static_url_path="", docs_dir=temp_dir
        )

        app.testing = True

        yield app


class TestPokemonEndpoint:
    @patch("pokepi.app.pokeapi_processor", return_value="original_description")
    @patch(
        "pokepi.app.shakespeare_processor",
        return_value="translated_description",
    )
    def test_ok(self, m_shakespeare_processor, m_pokeapi_processor, test_app):
        with test_app.test_client() as client:
            resp = client.get("/pokemon/pokemon_name")

            assert resp.status_code == 200
            assert resp.json == dict(
                name="pokemon_name", description="translated_description"
            )

            m_pokeapi_processor.assert_called_once_with("pokemon_name")
            m_shakespeare_processor.assert_called_once_with("original_description")

    @patch("pokepi.app.pokeapi_processor", side_effect=ResourceNotFound)
    @patch(
        "pokepi.app.shakespeare_processor",
    )
    def test_not_found(self, m_shakespeare_processor, m_pokeapi_processor, test_app):
        with test_app.test_client() as client:
            resp = client.get("/pokemon/not_found")

            assert resp.status_code == 404
            assert resp.json == dict(
                code=404,
                name="Not Found",
                description="The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
            )

            m_pokeapi_processor.assert_called_once_with("not_found")
            m_shakespeare_processor.assert_not_called()

    @patch("pokepi.app.pokeapi_processor", side_effect=ProviderError)
    @patch(
        "pokepi.app.shakespeare_processor",
    )
    def test_unexcpected_error(
        self, m_shakespeare_processor, m_pokeapi_processor, test_app
    ):
        with test_app.test_client() as client:
            resp = client.get("/pokemon/unexpected_error")

            assert resp.status_code == 500
            assert resp.json == dict(
                code=500,
                name="Internal Server Error",
                description="The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.",
            )

            m_pokeapi_processor.assert_called_once_with("unexpected_error")
            m_shakespeare_processor.assert_not_called()


class TestHealthCheck:
    def test_ok(self, test_app):
        with test_app.test_client() as client:
            resp = client.get("/health")

            assert resp.status_code == 200
            assert resp.json == dict(health="ok")


class TestDocumentation:
    def test_ok(self, test_app):
        with test_app.test_client() as client:
            resp = client.get("/docs")

            assert resp.status_code == 200
            assert resp.data == b"docs!"
