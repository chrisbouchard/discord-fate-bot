# Stage 1: Environment to build binary wheel

FROM kennethreitz/pipenv as build

ADD . /app
WORKDIR /app

RUN pipenv install --dev \
        && pipenv lock -r > requirements.txt \
        && pipenv run python setup.py bdist_wheel


# Stage 2: Environment to run bot

FROM python:3.7

WORKDIR /usr/src/app

COPY --from=build /app/dist/*.whl .
RUN pip install --no-cache-dir *.whl

CMD [ "python", "-m", "discord_fate_bot" ]

