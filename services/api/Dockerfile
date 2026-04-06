FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY database /app/database
COPY services/api /app/services/api

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -e /app/database -e /app/services/api

EXPOSE 8000
CMD ["uvicorn", "mt5_platform_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
