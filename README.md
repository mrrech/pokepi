# Pokepi

REST API to expose a Shakesperean description for any Pokemon, given its name.

```
GET /pokemon/<name> HTTP/1.1
...
Content-Type: application/json

HTTP/1.1 200 OK
...
Content-Type: application/json

{
  "name": "<name>",
  "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
  do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
  minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
  commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit
  esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
  non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
}
```

## Installation

To use this repository make sure you have installed on your local machine a
[Python 3.8.x](https://www.python.org/downloads/) distribution and
[Poetry](https://python-poetry.org/).

Then you should be able to run the following commands:

```
$ cd pokepi
$ poetry install
$ poetry shell
```

Poetry will create a virtualenv for you and install all the required
dependencies to let you run the project and poke around.

I used [pytest](https://docs.pytest.org/en/stable/), so once you activated the
venv as shown above you should be able to run all the tests with:

```
$ pytest tests
```

I included test coverage as I find it useful in general and especially when
you work with Python. I have also added
[Black](https://black.readthedocs.io/en/stable/),
[Pylint](https://www.pylint.org/), and
[isort](https://pycqa.github.io/isort/), to enforce linting and code
formatting. These tools are essential when you work in a team and
the code is shared among different developers.

I didn't add type annotation to the project though. Whilst I fully understand
the importance of a full-fledged algebraic type system as the ones you find in
several languages, I am not fully convinced of the gradual typing that has been
"recently" introduced in Python. For this reason, and being the API quite
simple, I preferred to keep the Python code not-typed. For more complex projects
it would be different, but probably I wouldn't choose Python for more complex
projects nowadays.

I configured the application to issue the log messages to the `stdout` and
format them as JSON objects. Logging to `stdout` is particularly suitable for
application running inside a container and formatting the messages as JSON
objects is handy when you have some log collector that will parse them.

The application is served by [Gunincorn](https://gunicorn.org/) a well
established and reliable application server.

The application itself is written using
[Flask](https://flask.palletsprojects.com/en/1.1.x/), not a fancy web framework
but a reliable one. I decided not to use an ASGI Python Web Framework, because
I am not completely sold to the async thing in the Python world.

Documentation has been generated using [pdoc](https://pdoc3.github.io/pdoc/) to
automatically extract `docstring`s from the source code.

Instead of a `Dockerfile` I added a `Earthfile`. [Earthly](https://earthly.dev/)
is a nice tool which gives you repeatable builds easily. You might think of it
as a merge between a `Dockerfile` and a `makefile`. I have been playing with
it lately to standardize builds (and especially builds for Python
projects), and I found it quite cool. Creating a build with it is much easier
than doing the same things via multi-stage Dockerfiles, and I thought that
anyone that can understand a Dockerfile can also understand a Earthfile.

To build the project using Earthly please [install
it](https://earthly.dev/get-earthly) and then simply issue the following
command:

```
$ earthly --build-arg TAG=<a_meaningful_tag> +build-pokepi
```

You will end up with two docker images on your local machine (if you are building
locally), such as:

```
$ docker images
REPOSITORY              TAG                 IMAGE ID       CREATED        SIZE
mrrech/pokepi        2021.03.07v10       229e480112dc   30 minutes ago 142MB
mrrech/pokepi/docs   2021.03.07v10       5e8884cb83ba   30 minutes ago 21.9MB
```

The first one is the image containing the service, the second one is an
`nginx:alpine` Docker image with the automatically generated documentation
copied inside it. You should be able to use them as follows:

```
$ docker run -it --rm --env GUNICORN_CMD_ARGS="--bind=0.0.0.0" -p 8000:8000 mrrech/pokepi:2021.03.07v10

$ docker run -it --rm -p 8080:80 mrrech/pokepi/docs:2021.03.07v10
```

## Improvements

Of course there are many ways in which this API could be improved. If it was
part of a larger APIs system or if I wanted to spend some more time on it  I
would:

- add an OpenAPI layer on top
- create some WSGI middlewares to standardize things like logging, error
  handling, health checks, etc. In such a scenario all my API applications
  should be wrapped by the same middlewares
- improve the way in which the application is configured (e.g. logging, ports,
  number of workers, etc). For configuration I prefer to use env-variables and
  some standard way to export them to the application
- configure Gunincorn to log also in JSON format
- distribute documentation not via a dedicated container, but in any other way
  the APIs ecosystem is set up

just to name a few.
