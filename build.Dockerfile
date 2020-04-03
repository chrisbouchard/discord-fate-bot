# Base off the CircleCI Python image, which also has Docker installed
ARG PYTHON_VERSION=3.8
FROM circleci/python:${PYTHON_VERSION}-buster

ENV DOCKER_CLI_EXPERIMENTAL=enabled
ARG DOCKER_APP_VERSION=0.8.0

# Install Docker App
RUN export OSTYPE="$(uname | tr A-Z a-z)" && \
        curl -fsSL --output "/tmp/docker-app-${OSTYPE}.tar.gz" "https://github.com/docker/app/releases/download/v${DOCKER_APP_VERSION}/docker-app-${OSTYPE}.tar.gz" && \
        tar xf "/tmp/docker-app-${OSTYPE}.tar.gz" -C /tmp/ && \
        mkdir -p ~/.docker/cli-plugins && \
        cp "/tmp/docker-app-plugin-${OSTYPE}" ~/.docker/cli-plugins/docker-app

# Install Poetry
ARG POETRY_VERSION=1.0.5
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

