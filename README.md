# FastAPI JWT Token Authentication

A comprehensive example of implementing JWT (JSON Web Token) authentication in FastAPI with Python.

## Features

- **JWT Token Authentication**: Secure token-based authentication using PyJWT
- **Token Blacklisting**: Secure logout functionality with token revocation
- **Protected Routes**: Secure endpoints requiring valid JWT tokens
- **Comprehensive Testing**: Full test suite with pytest and fixture patterns
- **Production Ready**: Environment variables, error handling, and security best practices
- **Bilingual Documentation**: Complete guides in English and Russian

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd authorization_types

# Install dependencies using Poetry
poetry install

# Set environment variables (optional - defaults provided)
export API_USERNAME="admin"
export API_PASSWORD="password"
export JWT_SECRET_KEY="your-super-secret-jwt-key"
```

### Running the Application

```bash
# Start the development server
poetry run uvicorn app.main:app --reload

# The API will be available at:
# - Main app: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Alternative docs: http://localhost:8000/redoc
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v
```

## API Usage Examples

### 1. Login to Get JWT Token

```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "password"
     }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "admin",
  "message": "Login successful"
}
```

### 2. Access Protected Route

```bash
curl -X GET "http://localhost:8000/protected" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "message": "This is a protected route",
  "data": "secret information accessible with JWT token",
  "authenticated_user": "admin"
}
```

### 3. Get User Information

```bash
curl -X GET "http://localhost:8000/me" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "username": "admin",
  "message": "User information retrieved successfully"
}
```

### 4. Logout (Blacklist Token)

```bash
curl -X POST "http://localhost:8000/logout" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

## API Endpoints

| Method | Endpoint     | Description                    | Authentication |
|--------|-------------|--------------------------------|----------------|
| GET    | `/`         | Root endpoint                  | None           |
| GET    | `/health`   | Health check                   | None           |
| GET    | `/public`   | Public route example           | None           |
| POST   | `/login`    | Login and get JWT token        | None           |
| GET    | `/protected`| Protected route example        | JWT Required   |
| GET    | `/me`       | Get current user info          | JWT Required   |
| POST   | `/logout`   | Logout and blacklist token     | JWT Required   |

## JWT Token Structure

Our JWT tokens contain the following claims:

```json
{
  "sub": "admin",                    // Subject (username)
  "exp": 1707324865,                 // Expiration timestamp
  "iat": 1707323065,                 // Issued at timestamp
  "jti": "random-unique-identifier"  // JWT ID for token tracking
}
```

## Configuration

### Environment Variables

| Variable        | Description                    | Default   |
|----------------|--------------------------------|-----------|
| `API_USERNAME` | Username for authentication    | `admin`   |
| `API_PASSWORD` | Password for authentication    | `password`|
| `JWT_SECRET_KEY`| Secret key for JWT signing    | Auto-generated |
| `DEBUG`        | Enable debug mode              | `True`    |

### Token Configuration

- **Token Expiration**: 30 minutes (default)
- **Algorithm**: HS256
- **Token Type**: Bearer
- **Blacklist Cleanup**: Automatic removal of expired tokens

## Security Features

### 1. Secure Password Comparison
Uses `secrets.compare_digest()` to prevent timing attacks:

```python
def validate_credentials(username: str, password: str) -> bool:
    return (secrets.compare_digest(username, settings.API_USERNAME) and 
            secrets.compare_digest(password, settings.API_PASSWORD))
```

### 2. JWT Token Security
- Strong secret key generation
- Token expiration validation
- Token blacklisting for logout
- Unique JWT ID (jti) for each token

### 3. HTTPS Recommendations
For production deployment:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify exact domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Testing

### Test Structure

The test suite includes:

- **Public endpoints**: Testing routes without authentication
- **JWT authentication flow**: Login, token validation, logout
- **Protected routes**: Testing with valid/invalid tokens
- **Error scenarios**: Malformed headers, expired tokens
- **Token blacklisting**: Logout functionality verification

### Example Test

```python
def test_protected_route_with_valid_token(client, auth_headers):
    """Test protected route with valid JWT token."""
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["authenticated_user"] == "admin"
```

### Test Fixtures

```python
@pytest.fixture
def auth_headers(login_user):
    """Create authorization headers with JWT token."""
    token = login_user.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## Architecture

### File Structure

```
authorization_types/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and routes
│   ├── auth.py          # JWT authentication logic
│   ├── config.py        # Configuration settings
│   └── models.py        # Pydantic models
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Test fixtures
│   └── test_auth_handlers.py  # Authentication tests
├── docs/
│   └── jwt_auth_explained.md   # Detailed documentation
├── pyproject.toml       # Project dependencies
└── README.md           # This file
```

### Dependencies

- **FastAPI**: Modern Python web framework
- **PyJWT**: JSON Web Token implementation
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI
- **Pytest**: Testing framework

## Comparison: JWT vs Session Authentication

| Feature              | JWT Tokens                 | Session Cookies           |
|---------------------|----------------------------|---------------------------|
| **Storage**         | Stateless (client-side)    | Server-side sessions      |
| **Scalability**     | Excellent (stateless)      | Requires session store    |
| **Security**        | Token-based, revokable     | Server-controlled         |
| **Expiration**      | Built-in expiration        | Server-managed TTL        |
| **Cross-domain**    | Easy with headers          | Requires CORS setup       |
| **Mobile apps**     | Native support             | Requires special handling |

## Documentation

For detailed information about JWT authentication implementation, see:

- **[JWT Token Authentication in FastAPI](docs/jwt_auth_explained.md)** - Complete bilingual documentation with implementation details, security considerations, and production deployment guide
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - Learn more about JSON Web Tokens

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

# FastAPI JWT Token Аутентификация

Комплексный пример реализации JWT (JSON Web Token) аутентификации в FastAPI с Python.

## Возможности

- **JWT Token Аутентификация**: Безопасная токен-ориентированная аутентификация с использованием PyJWT
- **Блэклист токенов**: Безопасная функция выхода с отзывом токенов
- **Защищенные маршруты**: Безопасные эндпоинты, требующие действительные JWT токены
- **Комплексное тестирование**: Полный набор тестов с pytest и паттернами фикстур
- **Готовность к продакшену**: Переменные окружения, обработка ошибок и лучшие практики безопасности
- **Двуязычная документация**: Полные руководства на английском и русском языках

## Быстрый старт

### Установка

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd authorization_types

# Установите зависимости с помощью Poetry
poetry install

# Установите переменные окружения (необязательно - предоставлены значения по умолчанию)
export API_USERNAME="admin"
export API_PASSWORD="password"
export JWT_SECRET_KEY="your-super-secret-jwt-key"
```

### Запуск приложения

```bash
# Запустите сервер разработки
poetry run uvicorn app.main:app --reload

# API будет доступен по адресу:
# - Основное приложение: http://localhost:8000
# - Интерактивная документация: http://localhost:8000/docs
# - Альтернативная документация: http://localhost:8000/redoc
```

### Запуск тестов

```bash
# Запустить все тесты
poetry run pytest

# Запустить тесты с подробным выводом
poetry run pytest -v
```

## Примеры использования API

### 1. Вход для получения JWT токена

```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "password"
     }'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "admin",
  "message": "Login successful"
}
```

### 2. Доступ к защищенному маршруту

```bash
curl -X GET "http://localhost:8000/protected" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Ответ:**
```json
{
  "message": "This is a protected route",
  "data": "secret information accessible with JWT token",
  "authenticated_user": "admin"
}
```

### 3. Получение информации о пользователе

```bash
curl -X GET "http://localhost:8000/me" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Ответ:**
```json
{
  "username": "admin",
  "message": "User information retrieved successfully"
}
```

### 4. Выход (блэклист токена)

```bash
curl -X POST "http://localhost:8000/logout" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Ответ:**
```json
{
  "message": "Logout successful"
}
```

## API Эндпоинты

| Метод  | Эндпоинт     | Описание                       | Аутентификация |
|--------|-------------|--------------------------------|----------------|
| GET    | `/`         | Корневой эндпоинт              | Нет            |
| GET    | `/health`   | Проверка состояния             | Нет            |
| GET    | `/public`   | Пример публичного маршрута     | Нет            |
| POST   | `/login`    | Вход и получение JWT токена    | Нет            |
| GET    | `/protected`| Пример защищенного маршрута    | JWT обязателен |
| GET    | `/me`       | Получение информации о пользователе | JWT обязателен |
| POST   | `/logout`   | Выход и блэклист токена        | JWT обязателен |

## Структура JWT токена

Наши JWT токены содержат следующие утверждения:

```json
{
  "sub": "admin",                    // Субъект (имя пользователя)
  "exp": 1707324865,                 // Временная метка истечения
  "iat": 1707323065,                 // Временная метка выдачи
  "jti": "random-unique-identifier"  // JWT ID для отслеживания токенов
}
```

## Конфигурация

### Переменные окружения

| Переменная      | Описание                       | По умолчанию |
|----------------|--------------------------------|--------------|
| `API_USERNAME` | Имя пользователя для аутентификации | `admin`   |
| `API_PASSWORD` | Пароль для аутентификации      | `password`   |
| `JWT_SECRET_KEY`| Секретный ключ для подписи JWT | Автогенерация |
| `DEBUG`        | Включить режим отладки         | `True`       |

### Конфигурация токенов

- **Истечение токена**: 30 минут (по умолчанию)
- **Алгоритм**: HS256
- **Тип токена**: Bearer
- **Очистка блэклиста**: Автоматическое удаление истекших токенов

## Функции безопасности

### 1. Безопасное сравнение паролей
Использует `secrets.compare_digest()` для предотвращения атак по времени:

```python
def validate_credentials(username: str, password: str) -> bool:
    return (secrets.compare_digest(username, settings.API_USERNAME) and 
            secrets.compare_digest(password, settings.API_PASSWORD))
```

### 2. Безопасность JWT токенов
- Генерация сильного секретного ключа
- Валидация истечения токена
- Блэклист токенов для выхода
- Уникальный JWT ID (jti) для каждого токена

### 3. Рекомендации HTTPS
Для развертывания в продакшене:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Укажите точные домены
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Тестирование

### Структура тестов

Набор тестов включает:

- **Публичные эндпоинты**: Тестирование маршрутов без аутентификации
- **Поток JWT аутентификации**: Вход, валидация токена, выход
- **Защищенные маршруты**: Тестирование с действительными/недействительными токенами
- **Сценарии ошибок**: Неправильные заголовки, истекшие токены
- **Блэклист токенов**: Проверка функции выхода

### Пример теста

```python
def test_protected_route_with_valid_token(client, auth_headers):
    """Тест защищенного маршрута с действительным JWT токеном."""
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["authenticated_user"] == "admin"
```

### Тестовые фикстуры

```python
@pytest.fixture
def auth_headers(login_user):
    """Создает заголовки авторизации с JWT токеном."""
    token = login_user.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## Архитектура

### Структура файлов

```
authorization_types/
├── app/
│   ├── __init__.py
│   ├── main.py          # Приложение FastAPI и маршруты
│   ├── auth.py          # Логика JWT аутентификации
│   ├── config.py        # Настройки конфигурации
│   └── models.py        # Модели Pydantic
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Тестовые фикстуры
│   └── test_auth_handlers.py  # Тесты аутентификации
├── docs/
│   └── jwt_auth_explained.md   # Подробная документация
├── pyproject.toml       # Зависимости проекта
└── README.md           # Этот файл
```

### Зависимости

- **FastAPI**: Современный Python веб-фреймворк
- **PyJWT**: Реализация JSON Web Token
- **Pydantic**: Валидация данных с использованием аннотаций типов Python
- **Uvicorn**: ASGI сервер для запуска FastAPI
- **Pytest**: Фреймворк для тестирования

## Сравнение: JWT против сессионной аутентификации

| Особенность          | JWT токены                     | Сессионные cookies        |
|---------------------|--------------------------------|---------------------------|
| **Хранение**        | Без состояния (клиентская сторона) | Серверные сессии        |
| **Масштабируемость** | Отличная (без состояния)      | Требует хранилище сессий  |
| **Безопасность**    | На основе токенов, отзывные    | Контролируемые сервером   |
| **Истечение**       | Встроенное истечение           | TTL управляемый сервером  |
| **Кросс-домен**     | Легко с заголовками            | Требует настройки CORS    |
| **Мобильные приложения** | Нативная поддержка        | Требует специальной обработки |

## Документация

Для подробной информации о реализации JWT аутентификации, смотрите:

- **[JWT Token Authentication in FastAPI](docs/jwt_auth_explained.md)** - Полная двуязычная документация с деталями реализации, соображениями безопасности и руководством по развертыванию в продакшене
- [Документация безопасности FastAPI](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - Узнайте больше о JSON Web Tokens

## Вклад в проект

1. Сделайте форк репозитория
2. Создайте ветку функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Лицензия

Этот проект лицензирован под лицензией MIT - смотрите файл LICENSE для деталей. 