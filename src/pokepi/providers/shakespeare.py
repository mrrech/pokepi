"""
Translate a given text to its Shakesperean's equivalent.
"""

import logging

import requests as rr
import schema

from pokepi.providers.common import RetryingSession


log = logging.getLogger(__name__)

URL = "https://api.funtranslations.com/translate/shakespeare.json"


VALIDATION_SCHEMA = schema.Schema(
    {
        "success": {"total": int},
        "contents": {"translated": str, "text": str, "translation": str},
    }
)


class TranslationError(Exception):
    "Generic translation error."


def get_translation(text):
    """
    Get translation from api.funtranslation.com
    """
    try:
        with RetryingSession() as http:
            resp = http.post(URL, data={"text": text})

        resp.raise_for_status()
    except rr.RequestException as exc:
        log.exception("Translation API failed with unexpected error: %s", exc)
        raise TranslationError() from None

    else:
        return resp.json()
