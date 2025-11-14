FROM python:3.13.0-slim-bookworm AS base

RUN useradd -ms /bin/bash appuser

USER root
RUN apt update && \
    apt -y install procps && \
    apt-get clean all && \
    rm -rf /var/lib/apt/lists/*
USER appuser

WORKDIR /var/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src
COPY entrypoint.py .

USER appuser
CMD ["python", "-u", "entrypoint.py"]
