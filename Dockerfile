# Dockerfile
FROM python:3.12-slim

# 1. Системные зависимости для psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# 2. Настройки Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Рабочая директория
WORKDIR /app

# 4. Устанавливаем poetry
RUN pip install --no-cache-dir poetry

# 5. Копируем лишь файлы зависимостей, чтобы кешировать слои
COPY pyproject.toml poetry.lock* /app/

# 6. Устанавливаем зависимости (только основные)
RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi

# 7. Копируем весь проект
COPY . /app

# (Опционально) соберём static, если нужно
# RUN python manage.py collectstatic --noinput

# 8. Команда по умолчанию (для dev)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
