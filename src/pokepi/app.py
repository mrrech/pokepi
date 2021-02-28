"""
Pokepi app.
"""
from flask import Flask, abort, json, jsonify
from werkzeug.exceptions import HTTPException

from pokepi.providers import ResourceNotFound, pokeapi_processor, shakespeare_processor


app = Flask(__name__)


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


@app.route("/pokemon/<name>")
def pokemon(name):
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


@app.route("/health")
def health():
    "Application's health-check endpoint."

    return jsonify({"health": "ok"})