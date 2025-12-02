FROM python:3.13.0-slim-bookworm AS base

RUN useradd -ms /bin/bash appuser

USER root
RUN apt-get update && \
    apt-get -y --no-install-recommends install procps=2:4.0.2-3 && \
    apt-get clean all && \
    rm -rf /var/lib/apt/lists/*
USER appuser

WORKDIR /var/app

FROM base AS script

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY entrypoint.py .

CMD ["python", "-u", "entrypoint.py"]

FROM base AS dev_base

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY src/ ./src
COPY entrypoint.py .
COPY docker-compose.yaml scripts/lint_and_test.sh scripts/format.sh ./

FROM dev_base AS lint_and_test

CMD ["./lint_and_test.sh"]

FROM dev_base AS format

CMD ["./format.sh"]
