# pylint: disable=no-self-use,missing-docstring

import pytest
import responses


@pytest.fixture(name="retrying_response")
def fixture_retrying_response():
    "Create Request mock targeting my own HTTP Adapter."
    with responses.RequestsMock(
        target="pokepi.providers.common.HTTPAdapterWithDefaultTimeout.send"
    ) as m_resp:
        yield m_resp
