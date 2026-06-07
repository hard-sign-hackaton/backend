FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && python scripts/local_add_mock_display.py && exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 20 --ws-ping-timeout 20"]