# Electronics Shop (Test Task)

Онлайн‑платформа торговой сети электроники.

![CI](https://github.com/<user>/<repo>/actions/workflows/ci.yml/badge.svg) <!-- Замените <user>/<repo> -->

---

## Содержание
- [Что реализовано](#-что-реализовано)
- [Стек](#-стек)
- [Быстрый старт](#-быстрый-старт)
  - [Docker](#вариант-1-docker-рекомендуется)
  - [Локально](#вариант-2-локально-без-docker)
- [Аутентификация (JWT)](#-аутентификация-jwt)
- [API Эндпоинты](#-api-эндпоинты)
- [Админ-панель](#-админ-панель)
- [Тесты и покрытие](#-тесты-и-покрытие)
  - [В Docker](#в-docker)
  - [Локально](#локально)
- [CI](#-ci)
- [Структура проекта](#-структура)
- [Полезные команды](#-полезные-команды)
- [Соответствие требованиям задания](#-задание-соответствие-требованиям)
- [Автор](#-автор)

---

## 🔧 Что реализовано

- **Модели**: `Partner` (звено сети: завод / розничная сеть / ИП) и `Product`.
- **Иерархия**: максимум 3 уровня, без циклов (валидация в `clean()`).
- **Админка**: вывод объектов, фильтр по городу, ссылка на поставщика, admin action для обнуления задолженности.
- **API (DRF)**: CRUD для партнёров, запрет изменения `debt_to_supplier` через API, фильтр по стране.
- **Доступ**: только активные `is_staff` пользователи. Аутентификация — JWT (SimpleJWT).
- **Документация API**: Swagger UI `/api/schema/swagger-ui/`, JSON схема `/api/schema/`.
- **Тесты**: для моделей, API и admin action. Покрытие измеряется coverage.
- **Docker / docker-compose** для быстрого запуска.
- **CI (GitHub Actions)**: автопрогон тестов и coverage на push/PR.

---

## 📦 Стек

- Python 3.12  
- Django 5.2  
- DRF 3.16  
- PostgreSQL 15  
- drf-spectacular, django-filter, djangorestframework-simplejwt  
- Poetry для зависимостей  
- GitHub Actions для CI

---

## 🚀 Быстрый старт

### Вариант 1. Docker (рекомендуется)

```bash
docker compose up --build
# далее (без пересборки):
docker compose up
```

Доступы:

- Приложение: http://localhost:8000/
- Админка: http://localhost:8000/admin/
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/

Создать суперпользователя:

```bash
docker compose exec web python manage.py createsuperuser
```

Остановить и удалить контейнеры:

```bash
docker compose down          # остановка
docker compose down -v       # + удаление volume (данные БД будут потеряны)
```

### Вариант 2. Локально (без Docker)

1. Установите PostgreSQL и создайте БД/пользователя:

   ```sql
   CREATE DATABASE electronics_db;
   CREATE USER electronics_user WITH PASSWORD 'postgres';
   GRANT ALL PRIVILEGES ON DATABASE electronics_db TO electronics_user;
   ```

2. Скопируйте `.env.example` → `.env` и заполните:

   ```bash
   cp .env.example .env
   ```

   ```env
   # Django
   SECRET_KEY=your-secret
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # DB
   POSTGRES_DB=electronics_db
   POSTGRES_USER=electronics_user
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   ```

3. Установите зависимости и запустите проект:

   ```bash
   poetry install --with dev
   poetry run python manage.py migrate
   poetry run python manage.py runserver
   ```

---

## 🔐 Аутентификация (JWT)

Получить токен:

```http
POST /api/token/
{
  "username": "admin",
  "password": "your-password"
}
```

Обновить токен:

```http
POST /api/token/refresh/
{
  "refresh": "<refresh_token>"
}
```

Добавляйте в запросы:

```http
Authorization: Bearer <access_token>
```

---

## 📚 API Эндпоинты

- `GET /api/partners/` — список (пагинация, фильтр `?country=RU`)
- `POST /api/partners/` — создать партнёра
- `GET /api/partners/{id}/` — получить
- `PATCH /api/partners/{id}/` — частично обновить (**поле `debt_to_supplier` read-only**)
- `DELETE /api/partners/{id}/` — удалить

Полная спецификация — в Swagger UI: `/api/schema/swagger-ui/`.

---

## 🛠 Админ-панель

- `/admin/`
- Фильтр по городу в списке партнёров.
- Ссылка на поставщика в карточке/списке.
- Action «Очистить задолженность перед поставщиком»:
  1. Отметить записи.
  2. Выбрать действие.
  3. Подтвердить.

---

## ✅ Тесты и покрытие

### В Docker

```bash
docker compose exec web poetry run coverage run manage.py test networks -v 2
docker compose exec web poetry run coverage report -m
docker compose exec web poetry run coverage html
```

### Локально

```bash
poetry run coverage run manage.py test networks -v 2
poetry run coverage report -m
poetry run coverage html   # отчёт: htmlcov/index.html
```

Порог покрытия находится в `.coveragerc` (`fail_under`, сейчас 85%).

---

## 🧪 CI

- Workflow: `.github/workflows/ci.yml`
- Прогоняет тесты и coverage на каждом push/PR в любую ветку.
- Артефакт HTML‑отчёта coverage прикрепляется к job.

---

## 📁 Структура

```
.
├── config/                 # настройки Django
├── networks/               # приложение (модели/сериализаторы/вью/тесты)
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .coveragerc
├── pyproject.toml
├── poetry.lock
├── .env.example
└── README.md
```

---

## 🧩 Полезные команды

```bash
# Миграции
python manage.py makemigrations
python manage.py migrate

# Суперпользователь
python manage.py createsuperuser

# OpenAPI JSON
/api/schema/
# Swagger UI
/api/schema/swagger-ui/
```

---

## 📌 Задание: соответствие требованиям

- Веб‑приложение + API + админка — ✅
- БД через миграции — ✅
- Модель сети (3 уровня) — ✅
- 1 поставщик для звена — ✅
- Поля звена, продукты, время создания — ✅
- Админка: вывод, фильтр по городу, ссылка на поставщика — ✅
- Admin action очистки долга — ✅
- API CRUD (без обновления долга) — ✅
- Фильтр по стране — ✅
- Доступ только для активных сотрудников — ✅

---

## 🙋 Автор

Святослав (Lorend359)  
GitHub: <https://github.com/Lorend359>  
Email: <arend359@gmail.com>
