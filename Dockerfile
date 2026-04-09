FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.15 /uv /uvx /bin/

COPY pyproject.toml uv.lock .python-version README.md ./

RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "python", "main.py"]
