FROM python:3.13.0-slim-bookworm AS base

RUN useradd -ms /bin/bash appuser

USER root
RUN apt-get update && \
    apt-get -y install procps && \
    apt-get clean all && \
    rm -rf /var/lib/apt/lists/*
USER appuser

WORKDIR /var/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY entrypoint.py .

USER appuser
CMD ["python", "-u", "entrypoint.py"]
