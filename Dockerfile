# Stage 1: Environment to build binary wheel

FROM python:3.7-buster as build

COPY . /app
WORKDIR /app

RUN apt-get update \
        && apt-get install -y --no-install-recommends pipenv=11.9.0-1 \
        && pipenv install --dev \
        && pipenv lock -r > requirements.txt \
        && pipenv run python setup.py bdist_wheel


# Stage 2: Environment to run bot

FROM python:3.7-buster

WORKDIR /usr/src/app

COPY --from=build /app/dist/*.whl .
RUN pip install --no-cache-dir ./*.whl

CMD [ "python", "-m", "discord_fate_bot" ]

