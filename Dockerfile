FROM python:3.13.0-slim-bookworm AS base

WORKDIR /var/app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src
COPY entrypoint.py .

RUN useradd -ms /bin/bash appuser
USER appuser
CMD ["python", "-u", "entrypoint.py"]
