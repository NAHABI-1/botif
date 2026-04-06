FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY services/engine /app/services/engine

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -e /app/services/engine

CMD ["python", "-c", "import mt5_platform_engine; print('engine ready')"]
