# syntax=docker/dockerfile:1

FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY requirements/ /tmp/requirements/
ARG REQUIREMENTS_FILE=requirements/local.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/${REQUIREMENTS_FILE} \
    && rm -rf /tmp/requirements

COPY --chown=app:app . /app

USER app

EXPOSE 8000

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
