# JWT Token Authentication in FastAPI

This guide provides a comprehensive overview of implementing JWT (JSON Web Token) authentication with refresh tokens in FastAPI applications.

## Table of Contents

- [English Guide](#english-guide)
  - [What is JWT Authentication?](#what-is-jwt-authentication)
  - [Refresh Token System](#refresh-token-system)
  - [Implementation Overview](#implementation-overview)
  - [Code Structure](#code-structure)
  - [API Endpoints](#api-endpoints)
  - [Testing JWT Authentication](#testing-jwt-authentication)
  - [Security Considerations](#security-considerations)
  - [Production Deployment](#production-deployment)
- [Russian Guide](#russian-guide)
  - [Что такое JWT аутентификация?](#что-такое-jwt-аутентификация)
  - [Система Refresh токенов](#система-refresh-токенов)
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

### Refresh Token System

Our implementation uses a dual-token approach for enhanced security and user experience:

**Access Tokens:**
- Short-lived (30 minutes default)
- Used for API authentication
- JWT format with signature verification
- Stored client-side

**Refresh Tokens:**
- Long-lived (7 days default)
- Used to obtain new access tokens
- Random secure string (not JWT)
- Stored both server-side and client-side

**Benefits:**
- **Security**: Short access token lifetime reduces exposure window
- **User Experience**: Long refresh tokens prevent frequent re-authentication
- **Revocation**: Immediate token invalidation on logout
- **Flexibility**: Different expiration policies for different token types

### Implementation Overview

Our JWT authentication system includes:

- **Token Creation**: Generate both access and refresh tokens on login
- **Token Validation**: Verify token signature and expiration
- **Token Refresh**: Exchange refresh token for new access token
- **Token Blacklisting**: Revoke tokens on logout for security
- **Protected Routes**: Secure endpoints requiring valid tokens
- **Automatic Cleanup**: Remove expired tokens from storage

### Code Structure

#### Authentication Module (`app/auth.py`)

```python
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple

# Token storage (use Redis in production)
blacklisted_tokens: Dict[str, datetime] = {}
refresh_tokens: Dict[str, Dict] = {}  # token -> {"username": str, "exp": datetime}

def create_token_pair(username: str) -> Tuple[str, str]:
    """Create both access and refresh tokens for the user."""
    access_token = create_jwt_token(username)
    refresh_token = create_refresh_token(username)
    return access_token, refresh_token

def create_jwt_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for the user."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)  # Short-lived
    
    payload = {
        "sub": username,  # Subject (user identifier)
        "exp": int(expire.timestamp()),    # Expiration time as Unix timestamp
        "iat": int(datetime.now(timezone.utc).timestamp()),  # Issued at
        "jti": secrets.token_urlsafe(16),   # JWT ID (unique identifier)
        "type": "access"  # Token type
    }
    
    return jwt.encode(payload, get_jwt_secret_key(), algorithm="HS256")

def create_refresh_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a refresh token for the user."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)  # Long-lived
    
    refresh_token = secrets.token_urlsafe(32)
    
    # Store refresh token info
    refresh_tokens[refresh_token] = {
        "username": username,
        "exp": expire
    }
    
    return refresh_token

def validate_refresh_token(refresh_token: str) -> str:
    """Validate refresh token and return username."""
    if refresh_token not in refresh_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    token_info = refresh_tokens[refresh_token]
    
    # Check if token is expired
    if token_info["exp"] < datetime.now(timezone.utc):
        # Remove expired token
        del refresh_tokens[refresh_token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    
    return token_info["username"]
```

#### Models (`app/models.py`)

```python
class LoginResponse(BaseModel):
    """Login response model with both access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    username: str
    message: str = "Login successful"

class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    """Refresh token response model with new access token."""
    access_token: str
    token_type: str = "bearer"
    message: str = "Token refreshed successfully"
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
    "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ",
    "token_type": "bearer",
    "username": "admin",
    "message": "Login successful"
}
```

#### 2. Token Refresh Endpoint
```http
POST /refresh
Content-Type: application/json

{
    "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ"
}
```

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "message": "Token refreshed successfully"
}
```

#### 3. Protected Endpoint
```http
GET /protected
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 4. Logout Endpoint
```http
POST /logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
    "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ"
}
```

### Testing JWT Authentication

#### Test Structure
```python
@pytest.fixture
def refresh_token(login_user):
    """Get refresh token from login response."""
    return login_user.json()["refresh_token"]

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

#### Running Tests
```bash
# Install dependencies
poetry install

# Run all tests
poetry run pytest
```

### Security Considerations

#### 1. Token Lifetimes
- **Access tokens**: Keep short (15-60 minutes) to limit exposure
- **Refresh tokens**: Longer (days/weeks) for user convenience
- **Balance**: Security vs. user experience

#### 2. Refresh Token Security
- **Storage**: Store refresh tokens securely server-side
- **Rotation**: Consider rotating refresh tokens on use
- **Revocation**: Immediate revocation on logout/suspicious activity
- **Not JWT**: Use random strings to prevent token inspection

#### 3. Access Token Security
- **JWT Benefits**: Stateless verification, embedded claims
- **Blacklisting**: Maintain blacklist for logout functionality
- **Secret Management**: Use strong, rotated secret keys

#### 4. Implementation Best Practices
```python
# Secure refresh token validation
def validate_refresh_token(refresh_token: str) -> str:
    if refresh_token not in refresh_tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    token_info = refresh_tokens[refresh_token]
    if token_info["exp"] < datetime.now(timezone.utc):
        del refresh_tokens[refresh_token]  # Clean up expired token
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    
    return token_info["username"]

# Secure logout with both tokens
async def logout(refresh_request: RefreshTokenRequest = None, 
                credentials: HTTPAuthorizationCredentials = Depends(security)):
    access_token = credentials.credentials
    blacklist_token(access_token)  # Blacklist access token
    
    if refresh_request and refresh_request.refresh_token:
        revoke_refresh_token(refresh_request.refresh_token)  # Revoke refresh token
```

### Production Deployment

#### Environment Variables
```bash
export JWT_SECRET_KEY="your-super-secret-key-here"
export API_USERNAME="your-username"
export API_PASSWORD="your-secure-password"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Redis Configuration (Recommended)
```python
# Replace in-memory storage with Redis
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def store_refresh_token(token: str, username: str, expires_in: timedelta):
    """Store refresh token in Redis with expiration."""
    redis_client.setex(
        f"refresh_token:{token}", 
        int(expires_in.total_seconds()),
        username
    )

def validate_refresh_token_redis(refresh_token: str) -> str:
    """Validate refresh token from Redis."""
    username = redis_client.get(f"refresh_token:{refresh_token}")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    return username.decode()
```

---

## Russian Guide

### Что такое JWT аутентификация?

JWT (JSON Web Token) - это компактный, URL-безопасный способ представления утверждений для передачи между двумя сторонами. Он состоит из трех частей, разделенных точками:

1. **Заголовок (Header)**: Содержит метаданные о типе токена и алгоритме подписи
2. **Полезная нагрузка (Payload)**: Содержит утверждения (данные пользователя и метаданные)
3. **Подпись (Signature)**: Используется для проверки того, что токен не был изменен

### Система Refresh токенов

Наша реализация использует двойную систему токенов для повышенной безопасности и пользовательского опыта:

**Access токены:**
- Короткоживущие (30 минут по умолчанию)
- Используются для аутентификации API
- Формат JWT с проверкой подписи
- Хранятся на клиентской стороне

**Refresh токены:**
- Долгоживущие (7 дней по умолчанию)
- Используются для получения новых access токенов
- Случайная безопасная строка (не JWT)
- Хранятся как на серверной, так и на клиентской стороне

**Преимущества:**
- **Безопасность**: Короткое время жизни access токена уменьшает окно уязвимости
- **Пользовательский опыт**: Долгие refresh токены предотвращают частую повторную аутентификацию
- **Отзыв**: Немедленная инвалидация токенов при выходе
- **Гибкость**: Различные политики истечения для разных типов токенов

### Обзор реализации

Наша система JWT аутентификации включает:

- **Создание токенов**: Генерация как access, так и refresh токенов при входе
- **Валидация токенов**: Проверка подписи токена и времени истечения
- **Обновление токенов**: Обмен refresh токена на новый access токен
- **Блэклист токенов**: Отзыв токенов при выходе для безопасности
- **Защищенные маршруты**: Безопасные эндпоинты, требующие действительные токены
- **Автоматическая очистка**: Удаление истекших токенов из хранилища

### Структура кода

#### Модуль аутентификации (`app/auth.py`)

```python
def create_token_pair(username: str) -> Tuple[str, str]:
    """Создает оба токена - access и refresh для пользователя."""
    access_token = create_jwt_token(username)
    refresh_token = create_refresh_token(username)
    return access_token, refresh_token

def create_refresh_token(username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Создает refresh токен для пользователя."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)  # Долгоживущий
    
    refresh_token = secrets.token_urlsafe(32)
    
    # Сохраняем информацию о refresh токене
    refresh_tokens[refresh_token] = {
        "username": username,
        "exp": expire
    }
    
    return refresh_token
```

### API эндпоинты

#### 1. Эндпоинт входа
Возвращает оба токена при успешном входе.

#### 2. Эндпоинт обновления токена
```http
POST /refresh
Content-Type: application/json

{
    "refresh_token": "a3B9d2F5c3RyaW5nX3JhbmRvbV92YWx1ZQ"
}
```

#### 3. Эндпоинт выхода
Принимает оба токена для полного выхода из системы.

### Соображения безопасности

#### 1. Время жизни токенов
- **Access токены**: Держите короткими (15-60 минут) для ограничения уязвимости
- **Refresh токены**: Длиннее (дни/недели) для удобства пользователя

#### 2. Безопасность Refresh токенов
- **Хранение**: Безопасное серверное хранение refresh токенов
- **Ротация**: Рассмотрите ротацию refresh токенов при использовании
- **Отзыв**: Немедленный отзыв при выходе/подозрительной активности

#### 3. Продакшен конфигурация
```python
# Использование Redis для продакшена
def store_refresh_token_redis(token: str, username: str, expires_in: timedelta):
    """Сохранить refresh токен в Redis с истечением."""
    redis_client.setex(
        f"refresh_token:{token}", 
        int(expires_in.total_seconds()),
        username
    )
```

### Продакшен развертывание

#### Переменные окружения
```bash
export JWT_SECRET_KEY="ваш-супер-секретный-ключ-здесь"
export API_USERNAME="ваш-логин"
export API_PASSWORD="ваш-безопасный-пароль"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Рекомендации по безопасности
- Используйте HTTPS в продакшене
- Храните refresh токены в Redis или базе данных
- Реализуйте ротацию токенов
- Мониторьте подозрительную активность
- Регулярно обновляйте секретные ключи
</rewritten_file>