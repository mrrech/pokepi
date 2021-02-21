"""
Retrieve Pokemon data from pokeapi.co
"""

import requests as rr
import schema


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


class ValidationError(Exception):
    "Invalid data structure"
    pass


def get_pokemon_species(name):
    """
    Call the remote provider pokeapi.co and return the result.

    If an error occure raise an exception.
    """
    url = URL.format(name=name)

    resp = rr.get(url)

    if not resp.ok:
        # TODO: deal with errors
        pass

    return resp.json()


def validate(payload):
    """
    Validate the PokeAPI result against the expected response schema.

    Since just few fields are actually required we make sure that just those
    fields are there and ignore the rest.
    """
    try:
        data = VALIDATION_SCHEMA.validate(payload)
    except schema.SchemaError as exc:
        raise ValidationError("Error validating the result") from exc

    return data


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
