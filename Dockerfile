# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1. Устанавливаем poetry
RUN pip install --no-cache-dir poetry

# 2. Копируем только файлы зависимостей для кеширования
COPY pyproject.toml poetry.lock* /app/

# 3. Ставим зависимости (только main)
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

# 4. Копируем проект
COPY . /app

# 5. Команда по умолчанию (dev)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
