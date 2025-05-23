# FastAPI Session Authentication

A simple implementation of Cookie-based Session Authentication in FastAPI.

## Overview

This project demonstrates how to implement Cookie-based Session Authentication in FastAPI without relying on external tools. Session authentication is handled through FastAPI's cookie dependencies and an in-memory session store.

## Project Structure

```
authorization_types/
├── app/
│   ├── __init__.py
│   ├── main.py        # Main application with FastAPI instance
│   ├── models.py      # Pydantic models
│   ├── auth.py        # Authentication implementation
│   ├── config.py      # Application settings
├── tests/
│   ├── __init__.py
│   ├── conftest.py    # Test fixtures
│   └── test_auth_handlers.py  # Authentication tests
├── docs/
│   └── session_auth_explained.md  # Detailed explanation
└── README.md
```

## Implementation Details

### Cookie-based Session Authentication
- Uses in-memory session storage (for simplicity)
- Login endpoint creates a session and sets a secure HTTP-only cookie
- Protected endpoints validate the session cookie
- Logout endpoint clears the session and removes the cookie
- For a detailed explanation, see [session_auth_explained.md](docs/session_auth_explained.md)

## Setup and Installation

1. Clone the repository
   
2. Install dependencies with Poetry:

```bash
# Install Poetry if you don't have it
pip install poetry==2.1.3

# Install dependencies
poetry install
```

## Configuration

Set the following environment variables or add them to a `.env` file:

```
API_USERNAME=admin      # Username for authentication
API_PASSWORD=password   # Password for authentication
```

## Running the Application

Start the server with:

```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Public Endpoints
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint
- `GET /public` - Example public endpoint (no auth required)

### Cookie-based Auth Endpoints
- `POST /login` - Login and create a session
- `GET /protected` - Protected endpoint (requires valid session cookie)
- `POST /logout` - Logout and end session

## Testing the Authentication

### Using curl

#### Cookie-based Authentication
```bash
# Login and save cookies to a file
curl -X POST http://localhost:8000/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"password"}' \
     -c cookies.txt

# Access protected endpoint using the saved cookies
curl -X GET http://localhost:8000/protected \
     -b cookies.txt

# Logout
curl -X POST http://localhost:8000/logout \
     -b cookies.txt
```

### Using the Test Suite

Run the automated test suite with:

```bash
poetry run pytest tests/test_auth_handlers.py -v
```

## Security Considerations

- **ALWAYS use HTTPS in production** - Authentication sends credentials that must be protected
- Don't hardcode credentials; use environment variables or a secure vault
- In production, use a persistent session store (Redis, database) instead of in-memory storage
- Set appropriate cookie security options (httpOnly, secure, sameSite)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

# Сессионная аутентификация в FastAPI

Простая реализация аутентификации на основе cookie-сессий в FastAPI.

## Обзор

Этот проект демонстрирует, как реализовать аутентификацию на основе cookie-сессий в FastAPI без использования внешних инструментов. Сессионная аутентификация обрабатывается с помощью cookie-зависимостей FastAPI и хранилища сессий в памяти.

## Структура проекта

```
authorization_types/
├── app/
│   ├── __init__.py
│   ├── main.py        # Основное приложение с экземпляром FastAPI
│   ├── models.py      # Модели Pydantic
│   ├── auth.py        # Реализация аутентификации
│   ├── config.py      # Настройки приложения
├── tests/
│   ├── __init__.py
│   ├── conftest.py    # Тестовые фикстуры
│   └── test_auth_handlers.py  # Тесты аутентификации
├── docs/
│   └── session_auth_explained.md  # Подробное объяснение
└── README.md
```

## Детали реализации

### Аутентификация на основе cookie-сессий
- Использует хранилище сессий в памяти (для простоты)
- Эндпоинт входа создает сессию и устанавливает безопасный HTTP-only cookie
- Защищенные эндпоинты проверяют наличие и валидность cookie сессии
- Эндпоинт выхода очищает сессию и удаляет cookie
- Для подробного объяснения смотрите [session_auth_explained.md](docs/session_auth_explained.md)

## Настройка и установка

1. Клонируйте репозиторий
   
2. Установите зависимости с помощью Poetry:

```bash
# Установите Poetry, если у вас его еще нет
pip install poetry==2.1.3

# Установите зависимости
poetry install
```

## Конфигурация

Установите следующие переменные окружения или добавьте их в файл `.env`:

```
API_USERNAME=admin      # Имя пользователя для аутентификации
API_PASSWORD=password   # Пароль для аутентификации
```

## Запуск приложения

Запустите сервер с помощью:

```bash
poetry run uvicorn app.main:app --reload
```

API будет доступен по адресу http://localhost:8000

## Эндпоинты API

### Публичные эндпоинты
- `GET /` - Корневой эндпоинт
- `GET /health` - Эндпоинт проверки работоспособности
- `GET /public` - Пример публичного эндпоинта (аутентификация не требуется)

### Эндпоинты с аутентификацией на основе cookie
- `POST /login` - Вход и создание сессии
- `GET /protected` - Защищенный эндпоинт (требуется валидный cookie сессии)
- `POST /logout` - Выход и завершение сессии

## Тестирование аутентификации

### Использование curl

#### Аутентификация на основе cookie
```bash
# Вход и сохранение cookies в файл
curl -X POST http://localhost:8000/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"password"}' \
     -c cookies.txt

# Доступ к защищенному эндпоинту с использованием сохраненных cookies
curl -X GET http://localhost:8000/protected \
     -b cookies.txt

# Выход
curl -X POST http://localhost:8000/logout \
     -b cookies.txt
```

### Использование набора тестов

Запустите автоматизированный набор тестов с помощью:

```bash
poetry run pytest tests/test_auth_handlers.py -v
```

## Соображения безопасности

- **ВСЕГДА используйте HTTPS в production** - Аутентификация отправляет учетные данные, которые должны быть защищены
- Не "хардкодьте" учетные данные; используйте переменные окружения или безопасное хранилище
- В production используйте постоянное хранилище сессий (Redis, база данных) вместо хранения в памяти
- Установите соответствующие параметры безопасности для cookie (httpOnly, secure, sameSite)

## Лицензия

Этот проект лицензирован под лицензией MIT - см. файл LICENSE для деталей. 