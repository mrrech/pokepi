"""
Retrieve Pokemon data from pokeapi.co
"""

import logging

import requests as rr
import schema

from pokepi.providers.common import (
    ProviderError,
    ResourceNotFound,
    RetryingSession,
    validate,
)


log = logging.getLogger(__name__)

URL = "https://pokeapi.co/api/v2/pokemon-species/{name}"
LANGUAGE = "en"

VALIDATION_SCHEMA = schema.Schema(
    {
        "flavor_text_entries": [
            {
                "flavor_text": str,
                "language": {"name": str, "url": str},
            }
        ]
    },
    ignore_extra_keys=True,
)


def get_pokemon_species(name):
    """
    Call the remote provider pokeapi.co and return the result.

    If an error occure raise an exception.
    """
    url = URL.format(name=name)

    try:
        with RetryingSession() as http:
            resp = http.get(url)

        resp.raise_for_status()
    except rr.HTTPError as exc:

        if exc.response.status_code == 404:
            raise ResourceNotFound(f"Pokemon '{name}' not found.") from None

        log.exception(
            "PokeAPI failed with HTTPError: %s, %s",
            exc.response.status_code,
            exc.response.reason,
        )
        raise ProviderError(
            "HTTP error from PokeAPI: %s, %s"
            % (exc.response.status_code, exc.response.reason)
        ) from None

    except rr.RequestException as exc:
        log.exception("PokeAPI failed with unexpected error: %s", exc)
        raise ProviderError("Unexpected error from PokeAPI") from None

    else:
        return resp.json()


def extract(payload):
    """
    Extract a brief description for the returned Pokemon Species.

    The API returns several descriptions in different languages, and for a given
    language more than one description can be available. Since we want to
    translate this description into Shakespeare's style only descriptions
    written in English are selected.
    """
    return [
        flavor["flavor_text"]
        for flavor in payload["flavor_text_entries"]
        if flavor["language"]["name"] == LANGUAGE
    ]


def sanitize(text):
    """
    Replace any whitespace-like charecter with a real space.

    Returned descriptions are sometimes plagued with new-lines, carriage return
    and other kinds of whitespace-like characters. We want to sanitize them
    before processing.

    `str.splitlines()` split a string at any occurence of a whitespace-like
    character, please refere to the
    [documentation](https://docs.python.org/3/library/stdtypes.html#str.splitlines).

    Note to the reader: what stated above has been inferred from a quick
    inspection of the results returned by the pokeapi.co service. In a
    real-world case the format of the returned data should be discussed with the
    external provider to understand what we should expect. If the provider
    cannot guarantee the quality of the data and precise text descriptions are
    required, there are some natural-language processing libraries that can be
    used.
    """
    soft_hyphens_normalized = text.replace("\xad\n", "").replace("-\n", "-")

    spaces_normilized = " ".join(soft_hyphens_normalized.splitlines())

    return spaces_normilized


def pokeapi_processor(name):
    """
    Return Pokemon's description when given a `name`.

    PokeAPI returns many descriptions for a given `name`, to make our API
    service really RESTful the result of this processor must be stable. One way
    to get it stable would have been to concatenate all the descriptions, but
    I'm not sure about any text length limit in the following translation step.
    So I decided to pick the longest description which should be fine.

    If the Pokemon does not exist a `ResourceNotFound` exception is raised. If
    the response does not conform to the expected JSON schema a
    `ValidationError` is raised. In case of any I/O error a generic
    `ProviderError` is raised. Unexcepted error conditions can raise any child
    of `Exception`.
    """
    payload = get_pokemon_species(name)

    validated = validate(payload, VALIDATION_SCHEMA)

    descriptions = extract(validated)

    sanitized = [sanitize(description) for description in descriptions]

    longest_description = sorted(sanitized, key=len, reverse=True)[0]

    return longest_description
