FROM python:3.13-alpine AS builder

RUN apk add --no-cache git

RUN pip install poetry==2.1.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry config repositories.github-csornyei-shared https://github.com/csornyei/finances_shared.git

RUN --mount=type=secret,id=github_user,env=GITHUB_USER \
    --mount=type=secret,id=github_token,env=GITHUB_TOKEN \
    poetry config http-basic.github-csornyei-shared $GITHUB_USER $GITHUB_TOKEN

RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install --without dev --no-root

FROM python:3.13-alpine AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src/tag_service ./tag_service

ENTRYPOINT ["fastapi", "run", "tag_service/main.py"]