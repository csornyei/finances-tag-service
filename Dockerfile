FROM python:3.13-alpine AS builder

RUN apk add --no-cache git

COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN touch README.md

RUN uv sync --no-dev --locked


FROM python:3.13-alpine AS runtime

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

COPY --from=builder /app/.venv ${VIRTUAL_ENV}

WORKDIR /app
COPY src/tag_service ./tag_service

ENTRYPOINT ["fastapi", "run", "tag_service/main.py"]