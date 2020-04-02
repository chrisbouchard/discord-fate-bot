FROM python:3.7-buster

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so we can cache this layer.
COPY requirements.txt .
RUN pip install --requirement requirements.txt

# Then install the wheel. We ignore DL3013 because it doesn't make sense to
# specify a version when installing a wheel.
COPY dist/*.whl .
# hadolint ignore=DL3013
RUN pip install ./*.whl

CMD [ "discord-fate-bot" ]

