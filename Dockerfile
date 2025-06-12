FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Применить миграции и запустить сервер
CMD alembic upgrade head && python -m src.main
