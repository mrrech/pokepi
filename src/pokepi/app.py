"""
Pokepi app.
"""
from pathlib import Path

from flask import Flask, abort, json, jsonify, send_from_directory
from flask.logging import default_handler
from pythonjsonlogger import jsonlogger
from werkzeug.exceptions import HTTPException

from pokepi.providers import ResourceNotFound, pokeapi_processor, shakespeare_processor


def pokepi_application_factory(app_name, static_url_path=None, docs_dir=None):
    """
    Create the pokepi Flask application.

    The returned Flask application exposes 3 endpoints:

        - `/health` which exposes a health-check endpoint
        - `/docs` which exposes the online documentation endpoint
        - `/pokemon/<name>` which exposes the actual Pokemon translation enpoint

    A custom handler is added to properly format all the HTTP exceptions as JSON
    responses.
    """
    flask_app = Flask(app_name, static_url_path=static_url_path)

    default_handler.setFormatter(
        jsonlogger.JsonFormatter(
            "%(levelname)s %(message)s %(module)s %(levelname)s %(lineno)s",
            timestamp=True,
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )

    @flask_app.errorhandler(HTTPException)
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

    @flask_app.route("/health")
    def health_endpoint():
        "Application's health-check endpoint."

        return jsonify({"health": "ok"})

    @flask_app.route("/docs")
    def docs_endpoint():
        "Serve the online documentation."

        return send_from_directory(docs_dir, "index.html")

    @flask_app.route("/pokemon/<name>")
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

    return flask_app


app = pokepi_application_factory(
    __name__, static_url_path="", docs_dir=Path("docs") / "pokepi"
)
