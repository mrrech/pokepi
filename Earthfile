#        __          __    __   __  __         __   __    __      __         __ ___
#       |__)/  \||  |  \  |__)||__)|_ |  ||\ ||_   |_ |  /  \|  |/  |__| /\ |__) |
#       |__)\__/||__|__/  |   ||   |__|__|| \||__  |  |__\__/|/\|\__|  |/--\| \  |
#
#
#                            +---------------+
#                            |               |
#  +----------------+        | Language base |-----------------------------+
#  |  Source code   |        |               |                             |
#  +----------------+        +---------------+                             |
#  |                |                |                                     |
#  |- Deps manifest |                v                                     |
#  |- src           |        +---------------+                             |
#  |- docs          |        |               |         PUSH                |
#  |- tests         |        |   Toolchain   |- - - - - - - - - - - > ...  |
#  |- ...           |        |               |      (artifact)             |
#  |                |        +---------------+                             |
#  +----------------+                |                                     |
#     |   |                          v                                     |
#                            +---------------+                             |
#     |   |   COPY           |               |           COPY              |
#         + - - - - - - - - >| Dependencies  |- - - - - - - - - - - - +    |
#     |  (manifest only)     |               |   (dependencies only)  |    |
#                            +---------------+                             |
#     |                              |                                |    |
#                                    v                                     |
#     |                      +---------------+                        |    |
#             COPY           |               |                             |
#     +- - - - - - - - - - ->|     Code      |                        |    |
#       (src, tests, etc)    |               |                             |
#                            +---------------+                        |    |
#                              | |   |   |                                 |
#          +-------------------+ |   |   |                            |    |
#          |          +----------+   |   +----+                            |
#          v          |           +--+        |                       |    |
#      +------+       v           |           v                       v    v
#      |      |   +-------+       |      +---------+               +---------------+
#      | Lint |   |       |       v      |         |     COPY      |               |
#      |      |   | Tests |   +------+   | Compile |- - - - - - - >|    Package    |
#      +------+   |       |   |      |   |         |("binary" only)|               |
#          |      +-------+   | Docs |   +---------+               +---------------+
#                     |       |      |                                 |   |
#          |                  +------+                         +-------+
#                     |           |                            |           | PUSH
#          v          v                                        v           + - - - - > ...
#                                 |                    +---------------+  (artifact)
#          SAVE REPORTS           v                    |  Integration  |
#          (for CI use)                                |               |
#                             SAVE DOCS                |     Tests     |
#                ^                                     +---------------+
#                |                                             |
#                +- - - - - - - - - - - - - - - - - - - - - - -+
#
# Notes:
#
# * Language Base:
#   - start from a (slim) public image
#   - possibly cache the public image in a local registry
#   - parametrize the version of the base image
#
# * Toolchain:
#   - add the required building tools (e.g. compilers, headers, libs, etc)
#   - if the Language Base image is missing build tools add and pin them here
#   - save the toolchain image for future CI run (updated every now and then)
#
#   NOTE:
#     Some languages, especially the older ones, lack a complete and/or easy to
#     use tooling suite (in the case of Python, for example, tools like pytest,
#     black, and poetry are not included with the language itself).
#
#     It would be better for these launguages to add the missing tools to the
#     toolchain image in order to close the gap between the older and the more
#     modern launguages and work as if they were all the same from here
#     downward in the pipeline. This is particularly true if you are working
#     within a mono-repo where many projects in several different launguages
#     are living along. In such a case having just one version of the building
#     tools is of great value.

#     However in the specific case of Python (and I guess of also other
#     "old-fashion" launguages in which the toolchain is a little bit clumsy)
#     the additional complexity to get this approach to work seamlessly is too
#     much (at least in my eyes) especially if the number of projects inside
#     the mono-repo is modest and/or the development team is just one (and/or
#     small). Let alone if you are not working in a mono-repo approach, in
#     which case you will have a number of Earthfiles anyway.
#
#     For all of these reasons I'll stick with the approach of declaring (and
#     pinnning) the toolchain dependencies as "dev-dependencies" at
#     repo/project level.
#
# * Dependencies:
#   - mount dependencies' manifest from "Source code"
#   - add project specific dependencies to the environment
#   - save the dependencies for re-use at the "Package" stage
#   - for launguages with a clumsy toolchain add build dependencies (as stated
#     above)
#
# * Code:
#   - mount actual source code, unit tests, docs, and whatever is required by
#     the build process
#
# * Compile:
#   - well... compile the code
#
#   NOTE:
#     Even launguages that don't require an actual compilation usually require
#     this step to build some sort of "binary" package (e.g. wheels for Python,
#     gems for Ruby, etc)
#
# * Lint/Test/Docs
#   - run the lint/test/docs phase and save the reports/artifacts
#
# * Package
#   - collect dependecies and the "binary" package and install them in the
#     "Language base" image
#   - save the image to the (local) registry
#
# * Integration Tests
#   - run integration tests by means Docker Compose (or a similar tool)

# Earthfile

ARG PYTHON_VERSION=3.8.8
ARG PYTHON_FLAVOUR=slim
ARG DEBIAN_VERSION=buster

FROM python:$PYTHON_VERSION-$PYTHON_FLAVOUR-$DEBIAN_VERSION

toolchain-python:
    # install compilers (for python dependencies including C code)
    RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -fr /var/lib/apt/lists/*

    # install specific version of poetry
    ARG POETRY_VERSION=1.1.5
    RUN pip --no-cache-dir install poetry==$POETRY_VERSION
    # configure poetry to create venvs inside the project dir
    RUN poetry config virtualenvs.in-project true

    SAVE IMAGE toolchain-python:latest

toolchain-python-dependencies:
    FROM +toolchain-python

    ARG SERVICE_NAME
    ARG SERVICE_DIR=/opt/$SERVICE_NAME

    WORKDIR $SERVICE_DIR

    COPY poetry.lock .
    COPY pyproject.toml .

    RUN poetry check

    RUN poetry install --no-root --no-dev && rm -fr $(poetry config cache-dir)/{cache,artifacts}

    SAVE ARTIFACT $SERVICE_DIR/.venv /_venv

    RUN poetry install --no-root && rm -fr $(poetry config cache-dir)/{cache,artifacts}

toolchain-python-code:
    FROM +toolchain-python-dependencies

    COPY ./ .

    RUN poetry install && rm -fr $(poetry config cache-dir)/{cache,artifacts}

toolchain-python-compile:
    FROM +toolchain-python-code

    RUN poetry build --format wheel

    SAVE ARTIFACT dist/ /_wheel

toolchain-python-lint:
    FROM +toolchain-python-code

    RUN poetry run pylint --output-format=parseable --exit-zero src > pylint-report.txt
    SAVE ARTIFACT pylint-report.txt AS LOCAL ./_ci/reports/pylint-report.txt

    RUN poetry run black --check src

toolchain-python-test:
    FROM +toolchain-python-code

    RUN poetry run pytest tests
    SAVE ARTIFACT pytest-xunit.xml AS LOCAL ./_ci/reports/pytest-xunit.xml
    SAVE ARTIFACT coverage.xml AS LOCAL ./_ci/reports/coverage.xml

toolchain-python-documentation:
    FROM +toolchain-python-code

    ARG SERVICE_NAME
    RUN poetry run pdoc --html --output-dir build-docs pokepi

    SAVE ARTIFACT build-docs/ /_docs

toolchain-python-shell:
    FROM +toolchain-python-code
    RUN false

toolchain-python-docker:
    ARG SERVICE_DOMAIN
    ARG SERVICE_NAME
    ARG TAG
    ARG SERVICE_DIR=/opt/$SERVICE_NAME
    ARG VENV_DIR=$SERVICE_DIR/.venv

    ARG TMP_WHEELS=/tmp/wheels

    COPY +toolchain-python-dependencies/_venv $VENV_DIR
    COPY +toolchain-python-compile/_wheel $TMP_WHEELS

    WORKDIR $SERVICE_DIR

    ENV PATH="$VENV_DIR/bin:$PATH"
    ENV PYTHONUNBUFFERED=1

    RUN pip --no-cache-dir install --no-deps $TMP_WHEELS/* && rm -fr $TMP_WHEELS

    RUN groupadd --system $SERVICE_NAME && useradd --create-home --system --gid $SERVICE_NAME $SERVICE_NAME
    USER $SERVICE_NAME

    EXPOSE 8000

    ENTRYPOINT ["$VENV_DIR/bin/gunicorn", "$SERVICE_NAME.app:app"]

    SAVE IMAGE --push $SERVICE_DOMAIN/$SERVICE_NAME:$TAG

toolchain-python-docker-documentation:
    FROM nginx:stable-alpine

    ARG SERVICE_DOMAIN
    ARG SERVICE_NAME
    ARG TAG

    # Copy the online documentation
    COPY +toolchain-python-documentation/_docs/* /usr/share/nginx/html

    EXPOSE 80
    SAVE IMAGE --push $SERVICE_DOMAIN/${SERVICE_NAME}/docs:$TAG

toolchain-python-build:
    BUILD +toolchain-python-lint
    BUILD +toolchain-python-test
    BUILD +toolchain-python-documentation
    BUILD +toolchain-python-docker
    BUILD +toolchain-python-docker-documentation

shell:
    ARG PROJECT=python
    BUILD +toolchain-$PROJECT-shell

build-pokepi:
    ARG SERVICE_DOMAIN=ariciputi
    ARG SERVICE_NAME=pokepi
    ARG TAG
    BUILD --build-arg SERVICE_NAME=$SERVICE_NAME \
          --build-arg SERVICE_DOMAIN=$SERVICE_DOMAIN \
          --build-arg TAG=$TAG \
          +toolchain-python-build

#
# Build invocation example
# ========================
#
# $ earthly --build-arg TAG=2021.01.05v1 +build-pokepi
