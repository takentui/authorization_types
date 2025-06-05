# GitHub OAuth 2.0 Authentication / Аутентификация через GitHub OAuth 2.0

## English

### Overview

This implementation provides GitHub OAuth 2.0 authentication alongside the existing JWT token system. Users can authenticate using their GitHub accounts and receive JWT tokens for subsequent API access.

### Features

- **GitHub OAuth 2.0 Flow**: Complete authorization code flow
- **JWT Integration**: OAuth users receive the same JWT tokens as regular users
- **User Management**: Automatic user creation and updates from GitHub data
- **Dual Authentication**: Works alongside existing username/password authentication
- **Email Access**: Optional access to user's GitHub email addresses
- **Error Handling**: Comprehensive error handling for OAuth failures

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI App    │    │   GitHub API    │
│                 │    │                  │    │                 │
│ 1. Get Auth URL │───▶│ GET /auth/github │    │                 │
│ 2. Redirect     │◀───│ Return auth_url  │    │                 │
│ 3. User Login   │────┼──────────────────┼───▶│ OAuth Login     │
│ 4. Callback     │◀───┼──────────────────┼────│ Return code     │
│ 5. Exchange     │───▶│ GET /callback    │───▶│ Exchange token  │
│ 6. Get JWT      │◀───│ Return JWT       │◀───│ User info       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Setup

#### 1. GitHub OAuth App Configuration

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the application details:
   - **Application name**: Your app name
   - **Homepage URL**: `http://localhost:8000` (for development)
   - **Authorization callback URL**: `http://localhost:8000/auth/github/callback`
4. Save the **Client ID** and **Client Secret**

#### 2. Environment Configuration

Create a `.env` file or set environment variables:

```bash
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback
```

### API Endpoints

#### 1. Initialize OAuth Flow

```http
GET /auth/github
```

**Response:**
```json
{
  "auth_url": "https://github.com/login/oauth/authorize?client_id=...",
  "state": "optional_state_parameter"
}
```

#### 2. Direct Redirect (Alternative)

```http
GET /auth/github/redirect
```

Returns a 307 redirect to GitHub authorization page.

#### 3. OAuth Callback

```http
GET /auth/github/callback?code=authorization_code&state=optional_state
```

**Success Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "refresh_token_string",
  "token_type": "bearer",
  "user": {
    "github_id": 123456,
    "username": "octocat",
    "display_name": "The Octocat",
    "email": "octocat@github.com",
    "avatar_url": "https://avatars.githubusercontent.com/u/583231",
    "profile_url": "https://github.com/octocat",
    "provider": "github",
    "created_at": "2023-01-01T00:00:00",
    "last_login": "2023-01-01T00:00:00"
  },
  "message": "OAuth login successful"
}
```

#### 4. Get OAuth User Info

```http
GET /auth/user
Authorization: Bearer your_jwt_token
```

**Response:**
```json
{
  "github_id": 123456,
  "username": "octocat",
  "display_name": "The Octocat",
  "email": "octocat@github.com",
  "avatar_url": "https://avatars.githubusercontent.com/u/583231",
  "profile_url": "https://github.com/octocat",
  "provider": "github",
  "created_at": "2023-01-01T00:00:00",
  "last_login": "2023-01-01T00:00:00"
}
```

### Usage Example

#### Frontend Implementation

```javascript
// 1. Initialize OAuth flow
const response = await fetch('/auth/github');
const { auth_url } = await response.json();

// 2. Redirect user to GitHub
window.location.href = auth_url;

// 3. Handle callback (automatically handled by backend)
// User will be redirected to /auth/github/callback
// Backend exchanges code for tokens and returns JWT

// 4. Store JWT tokens and use for API calls
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);

// 5. Use JWT for protected endpoints
const protectedResponse = await fetch('/protected', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

#### Backend Integration

OAuth users can use all existing JWT endpoints:
- `/protected` - Access protected resources
- `/refresh` - Refresh access tokens
- `/logout` - Logout and invalidate tokens
- `/me` - Get user information

### Error Handling

#### OAuth Errors

- **503 Service Unavailable**: GitHub OAuth not configured
- **400 Bad Request**: OAuth error from GitHub
- **502 Bad Gateway**: GitHub API communication error
- **500 Internal Server Error**: Unexpected OAuth processing error

#### Configuration Errors

If GitHub OAuth is not configured (missing CLIENT_ID or CLIENT_SECRET), endpoints will return:

```json
{
  "detail": "GitHub OAuth not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET"
}
```

### Security Considerations

1. **Client Secret**: Never expose GitHub Client Secret in frontend
2. **HTTPS**: Use HTTPS in production for OAuth callbacks
3. **State Parameter**: Implement CSRF protection using state parameter
4. **Token Storage**: Store JWT tokens securely (consider HttpOnly cookies)
5. **Scopes**: Request minimal necessary scopes from GitHub

### Testing

The implementation includes comprehensive tests:

```bash
# Run OAuth tests
pytest tests/test_oauth.py -v

# Run all tests
pytest -v
```

---

## Русский

### Обзор

Данная реализация предоставляет аутентификацию через GitHub OAuth 2.0 наряду с существующей системой JWT токенов. Пользователи могут аутентифицироваться с помощью своих GitHub аккаунтов и получать JWT токены для последующего доступа к API.

### Возможности

- **GitHub OAuth 2.0 Flow**: Полный поток авторизации
- **Интеграция с JWT**: OAuth пользователи получают те же JWT токены, что и обычные пользователи
- **Управление пользователями**: Автоматическое создание и обновление пользователей из данных GitHub
- **Двойная аутентификация**: Работает параллельно с существующей аутентификацией по логину/паролю
- **Доступ к email**: Опциональный доступ к email адресам пользователя в GitHub
- **Обработка ошибок**: Комплексная обработка ошибок OAuth

### Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Фронтенд      │    │   FastAPI App    │    │   GitHub API    │
│                 │    │                  │    │                 │
│ 1. Получить URL │───▶│ GET /auth/github │    │                 │
│ 2. Редирект     │◀───│ Вернуть auth_url │    │                 │
│ 3. Вход юзера   │────┼──────────────────┼───▶│ OAuth вход      │
│ 4. Колбэк       │◀───┼──────────────────┼────│ Вернуть код     │
│ 5. Обмен кода   │───▶│ GET /callback    │───▶│ Обменять токен  │
│ 6. Получить JWT │◀───│ Вернуть JWT      │◀───│ Инфо юзера      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Настройка

#### 1. Настройка GitHub OAuth App

1. Перейдите в GitHub Settings → Developer settings → OAuth Apps
2. Нажмите "New OAuth App"
3. Заполните информацию о приложении:
   - **Application name**: Название вашего приложения
   - **Homepage URL**: `http://localhost:8000` (для разработки)
   - **Authorization callback URL**: `http://localhost:8000/auth/github/callback`
4. Сохраните **Client ID** и **Client Secret**

#### 2. Настройка окружения

Создайте файл `.env` или установите переменные окружения:

```bash
GITHUB_CLIENT_ID=ваш_github_client_id
GITHUB_CLIENT_SECRET=ваш_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/auth/github/callback
```

### Эндпоинты API

#### 1. Инициализация OAuth потока

```http
GET /auth/github
```

**Ответ:**
```json
{
  "auth_url": "https://github.com/login/oauth/authorize?client_id=...",
  "state": "опциональный_state_параметр"
}
```

#### 2. Прямой редирект (альтернатива)

```http
GET /auth/github/redirect
```

Возвращает 307 редирект на страницу авторизации GitHub.

#### 3. OAuth колбэк

```http
GET /auth/github/callback?code=код_авторизации&state=опциональный_state
```

**Успешный ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "строка_refresh_токена",
  "token_type": "bearer",
  "user": {
    "github_id": 123456,
    "username": "octocat",
    "display_name": "The Octocat",
    "email": "octocat@github.com",
    "avatar_url": "https://avatars.githubusercontent.com/u/583231",
    "profile_url": "https://github.com/octocat",
    "provider": "github",
    "created_at": "2023-01-01T00:00:00",
    "last_login": "2023-01-01T00:00:00"
  },
  "message": "OAuth login successful"
}
```

#### 4. Получение информации о OAuth пользователе

```http
GET /auth/user
Authorization: Bearer ваш_jwt_токен
```

**Ответ:**
```json
{
  "github_id": 123456,
  "username": "octocat",
  "display_name": "The Octocat",
  "email": "octocat@github.com",
  "avatar_url": "https://avatars.githubusercontent.com/u/583231",
  "profile_url": "https://github.com/octocat",
  "provider": "github",
  "created_at": "2023-01-01T00:00:00",
  "last_login": "2023-01-01T00:00:00"
}
```

### Пример использования

#### Реализация на фронтенде

```javascript
// 1. Инициализация OAuth потока
const response = await fetch('/auth/github');
const { auth_url } = await response.json();

// 2. Перенаправление пользователя на GitHub
window.location.href = auth_url;

// 3. Обработка колбэка (автоматически обрабатывается бэкендом)
// Пользователь будет перенаправлен на /auth/github/callback
// Бэкенд обменивает код на токены и возвращает JWT

// 4. Сохранение JWT токенов и использование для API вызовов
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);

// 5. Использование JWT для защищенных эндпоинтов
const protectedResponse = await fetch('/protected', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

#### Интеграция с бэкендом

OAuth пользователи могут использовать все существующие JWT эндпоинты:
- `/protected` - Доступ к защищенным ресурсам
- `/refresh` - Обновление access токенов
- `/logout` - Выход и инвалидация токенов
- `/me` - Получение информации о пользователе

### Обработка ошибок

#### OAuth ошибки

- **503 Service Unavailable**: GitHub OAuth не настроен
- **400 Bad Request**: Ошибка OAuth от GitHub
- **502 Bad Gateway**: Ошибка связи с GitHub API
- **500 Internal Server Error**: Неожиданная ошибка обработки OAuth

#### Ошибки конфигурации

Если GitHub OAuth не настроен (отсутствует CLIENT_ID или CLIENT_SECRET), эндпоинты вернут:

```json
{
  "detail": "GitHub OAuth not configured. Please set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET"
}
```

### Соображения безопасности

1. **Client Secret**: Никогда не раскрывайте GitHub Client Secret во фронтенде
2. **HTTPS**: Используйте HTTPS в продакшене для OAuth колбэков
3. **State параметр**: Реализуйте защиту от CSRF с помощью state параметра
4. **Хранение токенов**: Храните JWT токены безопасно (рассмотрите HttpOnly cookies)
5. **Области доступа**: Запрашивайте минимально необходимые scopes от GitHub

### Тестирование

Реализация включает комплексные тесты:

```bash
# Запуск OAuth тестов
pytest tests/test_oauth.py -v

# Запуск всех тестов
pytest -v
``` 