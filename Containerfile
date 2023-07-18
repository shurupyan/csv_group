FROM python:3-slim as base

WORKDIR /app

COPY ./requirements.txt /tmp/requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app/src"

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /tmp

COPY ./src ./src

FROM base as backend

FROM base as test_backend
WORKDIR /app/src
