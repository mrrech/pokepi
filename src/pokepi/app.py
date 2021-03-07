"""
Pokepi app.
"""

from flask import Flask, abort, json, jsonify
from flask.logging import default_handler
from pythonjsonlogger import jsonlogger
from werkzeug.exceptions import HTTPException

from pokepi.providers import ResourceNotFound, pokeapi_processor, shakespeare_processor


app = Flask(__name__)

default_handler.setFormatter(
    jsonlogger.JsonFormatter(
        "%(levelname)s %(message)s %(module)s %(levelname)s %(lineno)s",
        timestamp=True,
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
)


@app.errorhandler(HTTPException)
def handle_exception(exception):
    """Return JSON instead of HTML for HTTP errors."""
    response = exception.get_response()
    response.data = json.dumps(
        {
            "code": exception.code,
            "name": exception.name,
            "description": exception.description,
        }
    )
    response.content_type = "application/json"
    return response


@app.route("/health")
def health_endpoint():
    "Application's health-check endpoint."

    return jsonify({"health": "ok"})


@app.route("/pokemon/<name>")
def pokemon_endpoint(name):
    "Return the Shakesperean description of the Pokemon named as `<name>`."

    try:
        description = pokeapi_processor(name)

        translated_description = shakespeare_processor(description)
    except ResourceNotFound as exc:
        app.logger.exception(exc)  # pylint: disable=no-member

        abort(404)
    except Exception as exc:  # pylint: disable=broad-except
        app.logger.exception(exc)  # pylint: disable=no-member

        abort(500)

    return jsonify({"name": name, "description": translated_description})
