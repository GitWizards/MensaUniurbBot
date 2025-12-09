FROM python:3.14-slim-trixie

ENV PYTHONUNBUFFERED 1

# UV settings
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1
ENV UV_PROJECT_ENVIRONMENT=/usr/local/

WORKDIR /app/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /uvx /bin/

# Install python requirements
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
