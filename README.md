# FastAPI JWT Token Authentication

A comprehensive example of implementing JWT (JSON Web Token) authentication in FastAPI with Python, including refresh token functionality.

## Features

- **JWT Token Authentication**: Secure token-based authentication using PyJWT
- **Refresh Token System**: Long-lived refresh tokens for seamless user experience
- **Token Blacklisting**: Secure logout functionality with token revocation
- **Protected Routes**: Secure endpoints requiring valid JWT tokens
- **Automatic Token Cleanup**: Prevents memory leaks from expired tokens
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

### 1. Login to Get JWT Tokens

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
  "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ",
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

### 3. Refresh Access Token

```bash
curl -X POST "http://localhost:8000/refresh" \
     -H "Content-Type: application/json" \
     -d '{
       "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ"
     }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "message": "Token refreshed successfully"
}
```

### 4. Get User Information

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

### 5. Logout (Blacklist Tokens)

```bash
# Logout with only access token
curl -X POST "http://localhost:8000/logout" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Logout with both access and refresh tokens
curl -X POST "http://localhost:8000/logout" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{
       "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ"
     }'
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

## API Endpoints

| Method | Endpoint     | Description                        | Authentication |
|--------|-------------|------------------------------------|--------------  |
| GET    | `/`         | Root endpoint                      | None           |
| GET    | `/health`   | Health check                       | None           |
| GET    | `/public`   | Public route example               | None           |
| POST   | `/login`    | Login and get JWT tokens           | None           |
| POST   | `/refresh`  | Refresh access token               | Refresh Token  |
| GET    | `/protected`| Protected route example            | JWT Required   |
| GET    | `/me`       | Get current user info              | JWT Required   |
| POST   | `/logout`   | Logout and blacklist tokens        | JWT Required   |

## Token System Architecture

### Access Tokens
- **Purpose**: Short-lived tokens for API access
- **Lifetime**: 30 minutes (default)
- **Format**: JWT with signature verification
- **Storage**: Client-side (localStorage, memory, etc.)

### Refresh Tokens
- **Purpose**: Long-lived tokens for obtaining new access tokens
- **Lifetime**: 7 days (default)
- **Format**: Random secure string
- **Storage**: Server-side store + client-side secure storage

### Token Structure

**Access Token (JWT):**
```json
{
  "sub": "admin",                    // Subject (username)
  "exp": 1707324865,                 // Expiration timestamp
  "iat": 1707323065,                 // Issued at timestamp
  "jti": "random-unique-identifier", // JWT ID for token tracking
  "type": "access"                   // Token type
}
```

**Refresh Token:**
- Cryptographically secure random string
- Stored server-side with expiration info
- Not a JWT (prevents token parsing attacks)

## Configuration

### Environment Variables

| Variable                | Description                     | Default      |
|-------------------------|---------------------------------|--------------|
| `API_USERNAME`          | Username for authentication     | `admin`      |
| `API_PASSWORD`          | Password for authentication     | `password`   |
| `JWT_SECRET_KEY`        | Secret key for JWT signing      | Auto-generated |
| `DEBUG`                 | Enable debug mode               | `True`       |
| `ACCESS_EXPIRE_MINUTES` | Living time of access token'а   | 30           |
| `REFRESH_EXPIRE_DAYS`   | Living time of refresh token'а  | 7            |


### Token Configuration

- **Access Token Expiration**: 30 minutes (default)
- **Refresh Token Expiration**: 7 days (default)
- **Algorithm**: HS256
- **Token Type**: Bearer
- **Automatic Cleanup**: Removes expired tokens from memory

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
- Access token blacklisting for logout
- Unique JWT ID (jti) for each token
- Token type identification

### 3. Refresh Token Security
- Cryptographically secure random generation
- Server-side storage and validation
- Automatic expiration and cleanup
- Immediate revocation on logout

### 4. HTTPS Recommendations
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
- **Refresh token flow**: Token refresh, expiration, invalid tokens
- **Protected routes**: Testing with valid/invalid tokens
- **Error scenarios**: Malformed headers, expired tokens
- **Token management**: Blacklisting and cleanup functionality

### Example Tests

```python
def test_refresh_token_flow_integration(client):
    """Test complete refresh token flow integration."""
    # 1. Login and get both tokens
    login_response = client.post("/login", json={"username": "admin", "password": "password"})
    tokens = login_response.json()
    
    # 2. Use access token
    auth_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
    
    # 3. Refresh access token
    refresh_response = client.post("/refresh", json={"refresh_token": tokens["refresh_token"]})
    new_token = refresh_response.json()["access_token"]
    
    # 4. Use new token
    new_headers = {"Authorization": f"Bearer {new_token}"}
    response = client.get("/protected", headers=new_headers)
    assert response.status_code == 200
```

### Test Fixtures

```python
@pytest.fixture
def refresh_token(login_user):
    """Get refresh token from login response."""
    return login_user.json()["refresh_token"]
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

## Token Flow Diagrams

### Login Flow
```
Client                    Server
  |                        |
  |--- POST /login ------>|
  |<-- access_token ------|
  |<-- refresh_token -----|
```

### Refresh Flow
```
Client                    Server
  |                        |
  |--- POST /refresh ---->| (with refresh_token)
  |<-- new access_token --|
```

### Logout Flow
```
Client                    Server
  |                        |
  |--- POST /logout ----->| (with access_token + refresh_token)
  |                       | - Blacklist access_token
  |                       | - Delete refresh_token
  |<-- logout success ----|
```

## Comparison: JWT vs Session Authentication

| Feature              | JWT + Refresh Tokens       | Session Cookies           |
|---------------------|----------------------------|-----------------------------|
| **Storage**         | Client + Server hybrid     | Server-side sessions        |
| **Scalability**     | Excellent (stateless access)| Requires session store     |
| **Security**        | Revokable + short-lived     | Server-controlled           |
| **Expiration**      | Dual-layer expiration       | Server-managed TTL          |
| **Cross-domain**    | Easy with headers           | Requires CORS setup         |
| **Mobile apps**     | Native support              | Requires special handling   |
| **Token refresh**   | Built-in refresh mechanism  | Session extension           |

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

Комплексный пример реализации JWT (JSON Web Token) аутентификации в FastAPI с Python, включая функциональность refresh токенов.

## Возможности

- **JWT Token Аутентификация**: Безопасная токен-ориентированная аутентификация с использованием PyJWT
- **Система Refresh токенов**: Долгоживущие refresh токены для бесшовного пользовательского опыта
- **Блэклист токенов**: Безопасная функция выхода с отзывом токенов
- **Защищенные маршруты**: Безопасные эндпоинты, требующие действительные JWT токены
- **Автоматическая очистка токенов**: Предотвращает утечки памяти от истекших токенов
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

### 1. Вход для получения JWT токенов

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
  "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ",
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

### 3. Обновление access токена

```bash
curl -X POST "http://localhost:8000/refresh" \
     -H "Content-Type: application/json" \
     -d '{
       "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ"
     }'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "message": "Token refreshed successfully"
}
```

### 4. Получение информации о пользователе

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

### 5. Выход (блэклист токенов)

```bash
# Выход только с access токеном
curl -X POST "http://localhost:8000/logout" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Выход с обоими токенами
curl -X POST "http://localhost:8000/logout" \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
     -H "Content-Type: application/json" \
     -d '{
       "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ"
     }'
```

**Ответ:**
```json
{
  "message": "Logout successful"
}
```

## API Эндпоинты

| Метод  | Эндпоинт     | Описание                           | Аутентификация |
|--------|-------------|------------------------------------|--------------  |
| GET    | `/`         | Корневой эндпоинт                  | Нет            |
| GET    | `/health`   | Проверка состояния                 | Нет            |
| GET    | `/public`   | Пример публичного маршрута         | Нет            |
| POST   | `/login`    | Вход и получение JWT токенов       | Нет            |
| POST   | `/refresh`  | Обновление access токена           | Refresh Token  |
| GET    | `/protected`| Пример защищенного маршрута        | JWT обязателен |
| GET    | `/me`       | Получение информации о пользователе| JWT обязателен |
| POST   | `/logout`   | Выход и блэклист токенов           | JWT обязателен |

## Архитектура системы токенов

### Access токены
- **Назначение**: Короткоживущие токены для доступа к API
- **Время жизни**: 30 минут (по умолчанию)
- **Формат**: JWT с проверкой подписи
- **Хранение**: Клиентская сторона (localStorage, память и т.д.)

### Refresh токены
- **Назначение**: Долгоживущие токены для получения новых access токенов
- **Время жизни**: 7 дней (по умолчанию)
- **Формат**: Случайная безопасная строка
- **Хранение**: Серверное хранилище + безопасное клиентское хранение

### Структура токенов

**Access Token (JWT):**
```json
{
  "sub": "admin",                    // Субъект (имя пользователя)
  "exp": 1707324865,                 // Временная метка истечения
  "iat": 1707323065,                 // Временная метка выдачи
  "jti": "random-unique-identifier", // JWT ID для отслеживания токенов
  "type": "access"                   // Тип токена
}
```

**Refresh Token:**
- Криптографически защищенная случайная строка
- Хранится на сервере с информацией об истечении
- Не является JWT (предотвращает атаки парсинга токенов)

## Конфигурация

### Переменные окружения

| Переменная              | Описание                           | По умолчанию  |
|-------------------------|------------------------------------|---------------|
| `API_USERNAME`          | Имя пользователя для аутентификации | `admin`       |
| `API_PASSWORD`          | Пароль для аутентификации          | `password`    |
| `JWT_SECRET_KEY`        | Секретный ключ для подписи JWT     | Автогенерация |
| `DEBUG`                 | Включить режим отладки             | `True`        |
| `ACCESS_EXPIRE_MINUTES` | Время жизни access token'а         | 30            |
| `REFRESH_EXPIRE_DAYS`   | Время жизни refresh token'а        | 7             |

### Конфигурация токенов

- **Истечение Access токена**: 30 минут (по умолчанию)
- **Истечение Refresh токена**: 7 дней (по умолчанию)
- **Алгоритм**: HS256
- **Тип токена**: Bearer
- **Автоматическая очистка**: Удаляет истекшие токены из памяти

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
- Блэклист access токенов для выхода
- Уникальный JWT ID (jti) для каждого токена
- Идентификация типа токена

### 3. Безопасность Refresh токенов
- Криптографически безопасная случайная генерация
- Серверное хранение и валидация
- Автоматическое истечение и очистка
- Немедленный отзыв при выходе

### 4. Рекомендации HTTPS
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
- **Поток Refresh токенов**: Обновление токена, истечение, недействительные токены
- **Защищенные маршруты**: Тестирование с действительными/недействительными токенами
- **Сценарии ошибок**: Неправильные заголовки, истекшие токены
- **Управление токенами**: Блэклист и функциональность очистки

## Документация

Для подробной информации о реализации JWT аутентификации, смотрите:

- **[JWT Token Authentication in FastAPI](docs/jwt_auth_explained.md)** - Полная двуязычная документация с деталями реализации, соображениями безопасности и руководством по развертыванию в продакшене
- [Документация безопасности FastAPI](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - Узнайте больше о JSON Web Tokens 