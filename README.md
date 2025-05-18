# FastAPI Basic Authentication

A simple implementation of HTTP Basic Authentication in FastAPI.

## Overview

This project demonstrates how to implement HTTP Basic Authentication directly in FastAPI without relying on external tools like Nginx. Basic authentication is handled through FastAPI's security utilities and dependency injection system.

## Project Structure

```
authorization_types/
├── app/
│   ├── __init__.py
│   ├── main.py        # Main application with FastAPI instance
│   ├── models.py      # Pydantic models
│   ├── auth.py        # Authentication implementation
│   ├── config.py      # Application settings
│   └── client.py      # Example external API client
├── tests/
│   ├── __init__.py
│   ├── conftest.py    # Test fixtures
│   └── test_auth_handlers.py  # Authentication tests
├── docs/
│   └── basic_auth_explained.md  # Detailed explanation
└── README.md
```

## Implementation Details

- HTTP Basic Authentication is implemented using FastAPI's `HTTPBasic` and `HTTPBasicCredentials`
- Authentication is performed using the `get_current_user` dependency
- Protected endpoints require this dependency
- Public endpoints don't include the dependency
- For a detailed explanation, see [basic_auth_explained.md](docs/basic_auth_explained.md)

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
API_USERNAME=admin      # Username for basic auth
API_PASSWORD=password   # Password for basic auth
```

## Running the Application

Start the server with:

```bash
poetry run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /` - Root endpoint (public)
- `GET /health` - Health check endpoint (public)
- `GET /public` - Example public endpoint (no auth required)
- `GET /protected` - Protected endpoint (requires basic auth)

## Testing the Authentication

### Using curl

```bash
# Test public endpoint
curl http://localhost:8000/public

# Test protected endpoint with authentication
curl -X GET http://localhost:8000/protected \
     -H "Authorization: Basic $(echo -n 'admin:password' | base64)"
```

### Using the Test Suite

Run the automated test suite with:

```bash
poetry run pytest tests/test_auth_handlers.py -v
```

## How Basic Auth Works

1. Client includes an `Authorization` header with the format: `Basic <base64-encoded-credentials>`
2. The base64-encoded part is the string `username:password`
3. FastAPI decodes and validates these credentials
4. If valid, the request proceeds; otherwise, a 401 Unauthorized response is returned

For a detailed explanation of the authentication process, see the [detailed documentation](docs/basic_auth_explained.md).

## Security Considerations

- **ALWAYS use HTTPS in production** - Basic auth sends credentials encoded (not encrypted)
- Don't hardcode credentials; use environment variables or a secure vault
- Consider using more secure methods (OAuth2, JWT) for production systems
- Basic auth is simple but has limitations (no token expiration, no granular permissions)

## Using Nginx for Basic Authentication

This project includes a ready-to-use Nginx configuration as an authentication gateway, which is a common production setup for securing multiple services.

### Running with Docker Compose

The repository already contains the necessary configuration files:
- `nginx/nginx.conf` - Nginx configuration with basic auth settings
- `nginx/.htpasswd` - Contains a test user (admin/admin) for demonstration

Simply run:

```bash
docker-compose up -d
```

### Accessing the API with Nginx

- Public endpoints: http://localhost/health (no authentication)
- Protected endpoints: http://localhost/ (requires basic auth)
  - Use username: `admin`
  - Password: `admin` (for demo only - change in production)

### Modifying Authentication

To add or change users:

```bash
# Add a new user
htpasswd nginx/.htpasswd newuser

# Change existing user's password
htpasswd nginx/.htpasswd admin
```

### Detailed Documentation

For a comprehensive guide on using Nginx as an authentication gateway for multiple services, including:
- Architecture diagrams
- Advanced configurations
- Security best practices
- Multiple service setup

See the detailed documentation: [Nginx Authentication Gateway Guide](docs/nginx_auth_gateway.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

# Базовая Аутентификация в FastAPI

Простая реализация HTTP Basic Authentication в FastAPI.

## Обзор

Этот проект демонстрирует, как реализовать HTTP Basic Authentication непосредственно в FastAPI без использования внешних инструментов, таких как Nginx. Базовая аутентификация обрабатывается с помощью утилит безопасности FastAPI и системы внедрения зависимостей.

## Структура проекта

```
authorization_types/
├── app/
│   ├── __init__.py
│   ├── main.py        # Основное приложение с экземпляром FastAPI
│   ├── models.py      # Модели Pydantic
│   ├── auth.py        # Реализация аутентификации
│   ├── config.py      # Настройки приложения
│   └── client.py      # Пример внешнего API-клиента
├── tests/
│   ├── __init__.py
│   ├── conftest.py    # Тестовые фикстуры
│   └── test_auth_handlers.py  # Тесты аутентификации
├── docs/
│   └── basic_auth_explained.md  # Подробное объяснение
└── README.md
```

## Детали реализации

- HTTP Basic Authentication реализована с использованием `HTTPBasic` и `HTTPBasicCredentials` из FastAPI
- Аутентификация выполняется с использованием зависимости `get_current_user`
- Защищенные эндпоинты требуют эту зависимость
- Публичные эндпоинты не включают эту зависимость
- Для подробного объяснения смотрите [basic_auth_explained.md](docs/basic_auth_explained.md)

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
API_USERNAME=admin      # Имя пользователя для базовой аутентификации
API_PASSWORD=password   # Пароль для базовой аутентификации
```

## Запуск приложения

Запустите сервер с помощью:

```bash
poetry run uvicorn app.main:app --reload
```

API будет доступен по адресу http://localhost:8000

## Эндпоинты API

- `GET /` - Корневой эндпоинт (публичный)
- `GET /health` - Эндпоинт проверки работоспособности (публичный)
- `GET /public` - Пример публичного эндпоинта (аутентификация не требуется)
- `GET /protected` - Защищенный эндпоинт (требуется базовая аутентификация)

## Тестирование аутентификации

### Использование curl

```bash
# Тест публичного эндпоинта
curl http://localhost:8000/public

# Тест защищенного эндпоинта с аутентификацией
curl -X GET http://localhost:8000/protected \
     -H "Authorization: Basic $(echo -n 'admin:password' | base64)"
```

### Использование набора тестов

Запустите автоматизированный набор тестов с помощью:

```bash
poetry run pytest tests/test_auth_handlers.py -v
```

## Как работает Basic Auth

1. Клиент включает заголовок `Authorization` в формате: `Basic <base64-закодированные-учетные-данные>`
2. Часть, закодированная в base64, представляет собой строку `username:password`
3. FastAPI декодирует и проверяет эти учетные данные
4. Если данные действительны, запрос продолжается; в противном случае возвращается ответ 401 Unauthorized

Для подробного объяснения процесса аутентификации см. [подробную документацию](docs/basic_auth_explained.md).

## Соображения безопасности

- **ВСЕГДА используйте HTTPS в production** - Basic auth отправляет учетные данные в кодированном (но не зашифрованном) виде
- Не "хардкодьте" учетные данные; используйте переменные окружения или безопасное хранилище
- Рассмотрите возможность использования более безопасных методов (OAuth2, JWT) для production систем
- Basic auth прост, но имеет ограничения (нет срока действия токена, нет детальных разрешений)

## Использование Nginx для базовой аутентификации

Этот проект включает готовую к использованию конфигурацию Nginx в качестве шлюза аутентификации, что является распространенной конфигурацией для обеспечения безопасности нескольких сервисов в production.

### Запуск с Docker Compose

Репозиторий уже содержит необходимые конфигурационные файлы:
- `nginx/nginx.conf` - Конфигурация Nginx с настройками базовой аутентификации
- `nginx/.htpasswd` - Содержит тестового пользователя (admin/admin) для демонстрации

Просто выполните:

```bash
docker-compose up -d
```

### Доступ к API через Nginx

- Публичные эндпоинты: http://localhost/health (без аутентификации)
- Защищенные эндпоинты: http://localhost/ (требует базовой аутентификации)
  - Имя пользователя: `admin`
  - Пароль: `admin` (только для демонстрации - измените в production)

### Изменение аутентификации

Чтобы добавить или изменить пользователей:

```bash
# Добавить нового пользователя
htpasswd nginx/.htpasswd newuser

# Изменить пароль существующего пользователя
htpasswd nginx/.htpasswd admin
```

### Подробная документация

Для получения полного руководства по использованию Nginx в качестве шлюза аутентификации для нескольких сервисов, включая:
- Схемы архитектуры
- Расширенные конфигурации
- Лучшие практики безопасности
- Настройку нескольких сервисов

См. подробную документацию: [Руководство по шлюзу аутентификации Nginx](docs/nginx_auth_gateway.md)

## Лицензия

Этот проект лицензирован под лицензией MIT - см. файл LICENSE для деталей. 