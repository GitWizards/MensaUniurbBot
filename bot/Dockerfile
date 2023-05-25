FROM python:3.11-slim-bullseye
MAINTAINER radeox "dawid.weglarz95@gmail.com"

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.5.0

WORKDIR /app/

# Generate Italian locales
RUN apt update && apt install locales -y && rm -rf /var/lib/apt/lists/*
RUN sed -i -e 's/# it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen && locale-gen

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Disable virtualenv inside container
RUN poetry config virtualenvs.create false

# Copy Python requirements
COPY poetry.lock pyproject.toml ./

# Install requirements
RUN poetry install --only main --no-interaction --no-ansi
