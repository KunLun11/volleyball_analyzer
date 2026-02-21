FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app 

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY app/ ./app/

RUN uv sync --frozen --no-dev 

FROM python:3.11-slim-bookworm

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app ./app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["/app/.venv/bin/granian", "--interface", "asgi", "app.web.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]