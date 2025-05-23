# JWT Token Authentication in FastAPI

This guide provides a comprehensive overview of implementing JWT (JSON Web Token) authentication in FastAPI applications.

## Table of Contents

- [English Guide](#english-guide)
  - [What is JWT Authentication?](#what-is-jwt-authentication)
  - [Implementation Overview](#implementation-overview)
  - [Code Structure](#code-structure)
  - [API Endpoints](#api-endpoints)
  - [Testing JWT Authentication](#testing-jwt-authentication)
  - [Security Considerations](#security-considerations)
  - [Production Deployment](#production-deployment)
- [Russian Guide](#russian-guide)
  - [Что такое JWT аутентификация?](#что-такое-jwt-аутентификация)
  - [Обзор реализации](#обзор-реализации)
  - [Структура кода](#структура-кода)
  - [API эндпоинты](#api-эндпоинты)
  - [Тестирование JWT аутентификации](#тестирование-jwt-аутентификации)
  - [Соображения безопасности](#соображения-безопасности)
  - [Продакшен развертывание](#продакшен-развертывание)

---

## English Guide

### What is JWT Authentication?

JWT (JSON Web Token) is a compact, URL-safe means of representing claims to be transferred between two parties. It consists of three parts separated by dots:

1. **Header**: Contains metadata about the token type and signing algorithm
2. **Payload**: Contains the claims (user data and metadata)
3. **Signature**: Used to verify the token hasn't been tampered with

**Example JWT Structure:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNzMyNDg2NX0.signature
│─────────── Header ────────────────││────────── Payload ───────────────────────││─ Signature ─│
```

### Implementation Overview

Our JWT authentication system includes:

- **Token Creation**: Generate JWT tokens with user claims and expiration
- **Token Validation**: Verify token signature and expiration
- **Token Blacklisting**: Revoke tokens on logout for security
- **Protected Routes**: Secure endpoints requiring valid tokens
- **Automatic Cleanup**: Remove expired tokens from blacklist

### Code Structure

#### Authentication Module (`app/auth.py`)

```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import secrets
from datetime import datetime, timedelta, timezone

# Token blacklist for logout functionality
blacklisted_tokens: Dict[str, datetime] = {}
security = HTTPBearer()

def create_jwt_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with user claims and expiration."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    payload = {
        "sub": username,  # Subject (user identifier)
        "exp": expire,    # Expiration time
        "iat": datetime.now(timezone.utc),  # Issued at
        "jti": secrets.token_urlsafe(16)    # JWT ID (unique identifier)
    }
    
    return jwt.encode(payload, get_jwt_secret_key(), algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract and validate the current user from JWT token."""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return username
```

#### Models (`app/models.py`)

```python
class LoginResponse(BaseModel):
    """Login response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    username: str
    message: str = "Login successful"
```

### API Endpoints

#### 1. Login Endpoint
```http
POST /login
Content-Type: application/json

{
    "username": "admin",
    "password": "password"
}
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

#### 2. Protected Endpoint
```http
GET /protected
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
    "message": "This is a protected route",
    "data": "secret information accessible with JWT token",
    "authenticated_user": "admin"
}
```

#### 3. User Info Endpoint
```http
GET /me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 4. Logout Endpoint
```http
POST /logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Testing JWT Authentication

#### Test Structure
```python
@pytest.fixture
def auth_headers(login_user):
    """Create authorization headers with JWT token."""
    token = login_user.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_protected_route_with_valid_token(client, auth_headers):
    """Test protected route with valid JWT token."""
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["authenticated_user"] == "admin"
```

#### Running Tests
```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app tests/
```

### Security Considerations

#### 1. Secret Key Management
- Use a strong, randomly generated secret key
- Store secret keys in environment variables
- Rotate keys regularly in production

```python
JWT_SECRET_KEY = secrets.token_urlsafe(32)  # Generate 32-byte key
```

#### 2. Token Expiration
- Set appropriate expiration times (15-60 minutes)
- Implement refresh token mechanism for longer sessions
- Balance security with user experience

#### 3. Token Blacklisting
- Blacklist tokens on logout for immediate revocation
- Clean up expired tokens to prevent memory leaks
- Consider using Redis for distributed applications

#### 4. HTTPS Only
```python
# In production, always use HTTPS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
)
```

### Production Deployment

#### Environment Variables
```bash
export JWT_SECRET_KEY="your-super-secret-key-here"
export API_USERNAME="your-username"
export API_PASSWORD="your-secure-password"
```

#### Docker Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install poetry
RUN poetry install --no-dev

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Nginx Configuration
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Authorization $http_authorization;
    }
}
```

---

## Russian Guide

### Что такое JWT аутентификация?

JWT (JSON Web Token) - это компактный, URL-безопасный способ представления утверждений для передачи между двумя сторонами. Он состоит из трех частей, разделенных точками:

1. **Заголовок (Header)**: Содержит метаданные о типе токена и алгоритме подписи
2. **Полезная нагрузка (Payload)**: Содержит утверждения (данные пользователя и метаданные)
3. **Подпись (Signature)**: Используется для проверки того, что токен не был изменен

**Пример структуры JWT:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTcwNzMyNDg2NX0.signature
│─────────── Заголовок ───────────││───────── Нагрузка ──────────││─ Подпись ─│
```

### Обзор реализации

Наша система JWT аутентификации включает:

- **Создание токенов**: Генерация JWT токенов с утверждениями пользователя и временем истечения
- **Валидация токенов**: Проверка подписи токена и времени истечения
- **Черный список токенов**: Отзыв токенов при выходе для безопасности
- **Защищенные маршруты**: Безопасные эндпоинты, требующие действительные токены
- **Автоматическая очистка**: Удаление истекших токенов из черного списка

### Структура кода

#### Модуль аутентификации (`app/auth.py`)

```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import secrets
from datetime import datetime, timedelta, timezone

# Черный список токенов для функции выхода
blacklisted_tokens: Dict[str, datetime] = {}
security = HTTPBearer()

def create_jwt_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Создает JWT токен с утверждениями пользователя и временем истечения."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    payload = {
        "sub": username,  # Субъект (идентификатор пользователя)
        "exp": expire,    # Время истечения
        "iat": datetime.now(timezone.utc),  # Время выдачи
        "jti": secrets.token_urlsafe(16)    # ID JWT (уникальный идентификатор)
    }
    
    return jwt.encode(payload, get_jwt_secret_key(), algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Извлекает и проверяет текущего пользователя из JWT токена."""
    token = credentials.credentials
    payload = decode_jwt_token(token)
    username = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительная нагрузка токена"
        )
    
    return username
```

#### Модели (`app/models.py`)

```python
class LoginResponse(BaseModel):
    """Ответ входа с JWT токеном."""
    access_token: str
    token_type: str = "bearer"
    username: str
    message: str = "Вход выполнен успешно"
```

### API эндпоинты

#### 1. Эндпоинт входа
```http
POST /login
Content-Type: application/json

{
    "username": "admin",
    "password": "password"
}
```

**Ответ:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "username": "admin",
    "message": "Вход выполнен успешно"
}
```

#### 2. Защищенный эндпоинт
```http
GET /protected
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ответ:**
```json
{
    "message": "Это защищенный маршрут",
    "data": "секретная информация, доступная с JWT токеном",
    "authenticated_user": "admin"
}
```

#### 3. Эндпоинт информации о пользователе
```http
GET /me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 4. Эндпоинт выхода
```http
POST /logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Тестирование JWT аутентификации

#### Структура тестов
```python
@pytest.fixture
def auth_headers(login_user):
    """Создает заголовки авторизации с JWT токеном."""
    token = login_user.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_protected_route_with_valid_token(client, auth_headers):
    """Тестирует защищенный маршрут с действительным JWT токеном."""
    response = client.get("/protected", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["authenticated_user"] == "admin"
```

#### Запуск тестов
```bash
# Установка зависимостей
poetry install

# Запуск всех тестов
poetry run pytest

# Запуск с покрытием
poetry run pytest --cov=app tests/
```

### Соображения безопасности

#### 1. Управление секретными ключами
- Используйте сильный, случайно сгенерированный секретный ключ
- Храните секретные ключи в переменных окружения
- Регулярно обновляйте ключи в продакшене

```python
JWT_SECRET_KEY = secrets.token_urlsafe(32)  # Генерация 32-байтного ключа
```

#### 2. Истечение токенов
- Установите подходящее время истечения (15-60 минут)
- Реализуйте механизм обновления токенов для длительных сессий
- Балансируйте безопасность с пользовательским опытом

#### 3. Черный список токенов
- Добавляйте токены в черный список при выходе для немедленного отзыва
- Очищайте истекшие токены для предотвращения утечек памяти
- Рассмотрите использование Redis для распределенных приложений

#### 4. Только HTTPS
```python
# В продакшене всегда используйте HTTPS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
)
```

### Продакшен развертывание

#### Переменные окружения
```bash
export JWT_SECRET_KEY="ваш-супер-секретный-ключ-здесь"
export API_USERNAME="ваш-логин"
export API_PASSWORD="ваш-безопасный-пароль"
```

#### Конфигурация Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install poetry
RUN poetry install --no-dev

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Конфигурация Nginx
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Authorization $http_authorization;
    }
} 