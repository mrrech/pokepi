"""
Wire utilities used by providers' implementations.
"""

import contextlib

import requests as rr
import schema
import urllib3


class HTTPAdapterWithDefaultTimeout(rr.adapters.HTTPAdapter):
    """
    Set a default timeout if one is not explicitly passed either to the Adapter or to the request.

    The default timeout is (6.1, 15) [connection timeout, read timeout]

    For further documentation please read:
        https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
    """

    default_timeout = (6.1, 15)

    def __init__(self, *args, **kwargs):
        self.timeout = self.default_timeout
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(  # pylint: disable=too-many-arguments
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        """
        Calls the `HTTPAdapter.send()` making sure a timeout is set.
        """
        return super().send(
            request,
            stream=stream,
            timeout=self.timeout if timeout is None else timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
        )


@contextlib.contextmanager
def RetryingSession(  # pylint: disable=invalid-name
    max_retries=5, status_forcelist=(500, 502, 503, 504), backoff_factor=2
):
    """
    HTTP Session that retries on specific response status codes.
    """

    retry_strategy = urllib3.Retry(
        total=max_retries,
        status_forcelist=status_forcelist,
        backoff_factor=backoff_factor,
    )
    adapter = HTTPAdapterWithDefaultTimeout(max_retries=retry_strategy)

    session = rr.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        yield session
    finally:
        session.close()


class ResourceNotFound(Exception):
    """
    Resource not found.

    This exception is usually raised when a provider reply with a 404 status
    code, meaning the requested resource was not found.
    """


class ProviderError(Exception):
    "Generic provider error."


class ValidationError(Exception):
    "Invalid data structure"


def validate(payload, validation_schema):
    """
    Validate the PokeAPI result against the expected response schema.

    Since just few fields are actually required we make sure that just those
    fields are there and ignore the rest.
    """
    try:
        data = validation_schema.validate(payload)
    except schema.SchemaError as exc:
        raise ValidationError("Error validating the result") from exc

    return data
