# syntax=docker/dockerfile:1

# -----------------------------
# 共通ステージ
# -----------------------------
FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /usr/src/app

# -----------------------------
# 依存関係のインストール
# -----------------------------
FROM base AS builder

RUN python -m venv /opt/venv

COPY requirements.txt ./

RUN pip install --upgrade pip \
    && pip install --requirement requirements.txt

# -----------------------------
# 開発環境
# -----------------------------
FROM base AS development

COPY --from=builder /opt/venv /opt/venv

RUN groupadd --gid 10001 appgroup \
    && useradd \
        --uid 10001 \
        --gid appgroup \
        --no-create-home \
        --shell /usr/sbin/nologin \
        appuser

COPY --chown=appuser:appgroup app/ ./
COPY --chown=appuser:appgroup tests/ /usr/src/tests/

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -----------------------------
# 本番環境
# -----------------------------
FROM base AS production

COPY --from=builder /opt/venv /opt/venv

RUN groupadd --gid 10001 appgroup \
    && useradd \
        --uid 10001 \
        --gid appgroup \
        --no-create-home \
        --shell /usr/sbin/nologin \
        appuser

COPY --chown=appuser:appgroup app/ ./

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]