FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED 1

# UV settings
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
ENV UV_PROJECT_ENVIRONMENT=/usr/local/

WORKDIR /app/

# Generate Italian locales
RUN apt update && apt install locales -y && rm -rf /var/lib/apt/lists/*
RUN sed -i -e 's/# it_IT.UTF-8 UTF-8/it_IT.UTF-8 UTF-8/' /etc/locale.gen && locale-gen

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.9 /uv /uvx /bin/

# Install python requirements
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
