# pylint: disable=no-self-use,missing-docstring

import pytest
import requests as rr

from pokepi.providers.common import RetryingSession


class TestRetryingSession:
    def test_always_fails(self, httpserver):
        httpserver.expect_request("/broken-api").respond_with_data(status=500)

        with pytest.raises(rr.exceptions.RetryError):
            with RetryingSession(max_retries=1) as http:
                http.get(httpserver.url_for("/broken-api"))

    def test_eventually_succeed(self, httpserver):
        data = {"result": "ok"}

        httpserver.expect_ordered_request("/flaky-api").respond_with_data(status=500)
        httpserver.expect_ordered_request("/flaky-api").respond_with_json(
            data, status=200
        )

        with RetryingSession(max_retries=1) as http:
            resp = http.get(httpserver.url_for("/flaky-api"))

            assert resp.status_code == 200
            assert resp.json() == data

    def test_dont_retry(self, httpserver):
        data = {"error": "not found"}

        httpserver.expect_request("/not-found-api").respond_with_json(data, status=404)

        with RetryingSession(max_retries=1) as http:
            resp = http.get(httpserver.url_for("/not-found-api"))

            assert resp.status_code == 404
            assert resp.json() == data
