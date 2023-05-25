FROM python:3.11-slim-bullseye
MAINTAINER radeox "dawid.weglarz95@gmail.com"

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.5.0

WORKDIR /app/

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Disable virtualenv inside container
RUN poetry config virtualenvs.create false

# Copy Python requirements
COPY poetry.lock pyproject.toml ./

# Install requirements
RUN poetry install --only main --no-interaction --no-ansi
