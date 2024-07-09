FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.8.3

WORKDIR /app/

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Disable virtualenv inside container
RUN poetry config virtualenvs.create false

# Copy Python requirements
COPY poetry.lock pyproject.toml ./

# Install requirements
RUN poetry install --only main --no-interaction --no-ansi
