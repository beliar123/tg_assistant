# ===================== STAGE 1: dockerize binary =====================
FROM alpine:3.21 AS dockerize-downloader

ARG DOCKERIZE_VERSION=v0.9.2

RUN apk add --no-cache wget \
  && wget -q "https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && tar -C /usr/local/bin -xzf "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && rm "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz"

# ===================== STAGE 2: Python dependencies =====================
FROM python:3.12-slim-bookworm AS deps-builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /code

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev

# ===================== STAGE 3: runtime =====================
FROM python:3.12-slim-bookworm AS runtime

ARG UID=1001
ARG GID=1001

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    TZ="Europe/Moscow" \
    PATH="/code/.venv/bin:/usr/local/bin:$PATH"

COPY --from=dockerize-downloader /usr/local/bin/dockerize /usr/local/bin/dockerize
COPY --from=deps-builder /code/.venv /code/.venv

RUN groupadd -r -g ${GID} tg_bot \
  && useradd -r -u ${UID} -g tg_bot -d /code tg_bot \
  && chown tg_bot:tg_bot /code

USER tg_bot:tg_bot

WORKDIR /code

COPY --chown=tg_bot:tg_bot src /code/src
COPY --chown=tg_bot:tg_bot scripts/schedule_entrypoint.sh /code/

RUN chmod +x /code/schedule_entrypoint.sh
