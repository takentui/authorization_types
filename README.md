# FastAPI Keycloak Authentication

A comprehensive example of implementing Keycloak authentication in FastAPI with Python, including Docker support and in-memory data storage.

## Features

- **Keycloak Integration**: Secure authentication using Keycloak OpenID Connect
- **In-Memory Storage**: Simple dictionary-based storage for development
- **Docker Support**: Complete Docker and docker-compose setup
- **Protected Routes**: Secure endpoints requiring valid Keycloak tokens
- **User Management**: Store and manage user information in memory
- **Session Management**: Track user sessions with token validation
- **Comprehensive Testing**: Full test suite with pytest and Keycloak mocking
- **Production Ready**: Environment variables, error handling, and security best practices

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for development)
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd authorization_types

# Make the startup script executable
chmod +x scripts/start.sh

# Start the entire application stack
./scripts/start.sh
```

### Manual Setup (Alternative)

```bash
# Start services with docker-compose
docker-compose up -d

# Initialize Keycloak (after Keycloak is ready)
python3 scripts/init_keycloak.py

# The API will be available at:
# - Main app: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - Keycloak console: http://localhost:8080
```

### Development Setup

```bash
# Install dependencies using pip
pip install -e .

# Set environment variables (optional - defaults provided)
export KEYCLOAK_SERVER_URL="http://localhost:8080"
export KEYCLOAK_REALM="master"
export KEYCLOAK_CLIENT_ID="fastapi-app"
export KEYCLOAK_CLIENT_SECRET="your-client-secret"

# Run the development server
uvicorn app.main:app --reload
```

## Docker Configuration

The application uses a multi-service Docker setup:

### Services

- **app**: FastAPI application
- **keycloak**: Keycloak authentication server (with embedded H2 database)

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KEYCLOAK_SERVER_URL` | Keycloak server URL | `http://localhost:8080` |
| `KEYCLOAK_REALM` | Keycloak realm name | `master` |
| `KEYCLOAK_CLIENT_ID` | Keycloak client ID | `fastapi-app` |
| `KEYCLOAK_CLIENT_SECRET` | Keycloak client secret | `your-client-secret` |
| `DEBUG` | Enable debug mode | `False` |

## API Usage Examples

### 1. Login to Get Keycloak Token

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
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJf...",
  "token_type": "bearer",
  "username": "admin",
  "message": "Login successful"
}
```

### 2. Access Protected Route

```bash
curl -X GET "http://localhost:8000/protected" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "message": "This is a protected route",
  "data": "secret information accessible with Keycloak token",
  "authenticated_user": "admin"
}
```

### 3. Get User Information

```bash
curl -X GET "http://localhost:8000/me" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "username": "admin",
  "user_data": {
    "username": "admin",
    "email": "admin@example.com",
    "keycloak_id": "user-id-from-keycloak",
    "roles": ["user", "admin"],
    "created_at": "2023-01-01T00:00:00"
  },
  "message": "User information retrieved successfully"
}
```

### 4. Logout

```bash
curl -X POST "http://localhost:8000/logout" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth_handlers.py

# Run with coverage
pytest --cov=app tests/
```

### Test Structure

The test suite includes:

- **Authentication flow**: Login, token validation, logout
- **Protected routes**: Testing with valid/invalid tokens
- **User management**: Database operations and user info
- **Error scenarios**: Invalid credentials, expired tokens
- **Keycloak integration**: Mocked Keycloak responses

## Architecture

### Components

1. **FastAPI Application** (`app/main.py`)
   - API endpoints and request handling
   - Authentication middleware integration
   - Error handling and response formatting

2. **Keycloak Integration** (`app/keycloak/`)
   - Keycloak client for authentication operations
   - Token validation and user info retrieval
   - Authentication dependencies for protected routes

3. **In-Memory Storage** (`app/database/`)
   - Dictionary-based in-memory storage for development
   - User and session data models
   - Thread-safe database operations

4. **Configuration** (`app/config.py`)
   - Environment-based configuration management
   - Keycloak connection settings
   - Application-wide settings

### Authentication Flow

1. User submits credentials to `/login`
2. FastAPI forwards credentials to Keycloak
3. Keycloak validates and returns access token
4. FastAPI stores user info in memory
5. Client uses access token for protected routes
6. FastAPI validates token with Keycloak on each request
7. User sessions are tracked in memory for quick access

## Security Features

### 1. Keycloak Integration
- Industry-standard OpenID Connect authentication
- Centralized user management and security policies
- Token-based authentication with automatic expiration
- Support for multi-factor authentication (configured in Keycloak)

### 2. Token Security
- JWT tokens with digital signatures
- Automatic token expiration handling
- Secure token transmission over HTTPS (in production)
- Token validation on every protected request

### 3. Local Data Protection
- Thread-safe database operations
- In-memory data storage (no file I/O)
- Session tracking with automatic cleanup
- Minimal data storage (only essential user info)

### 4. Production Recommendations

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

- Use HTTPS for all communications
- Configure proper CORS policies
- Set up Keycloak with SSL/TLS
- Use a proper database (PostgreSQL, MySQL) instead of in-memory storage
- Implement proper logging and monitoring
- Set up Keycloak realm-specific configuration

## Keycloak Configuration

### Default Setup

The initialization script creates:

- **Realm**: `master` (using default)
- **Client**: `fastapi-app` with client credentials
- **Users**: `admin` and `testuser` with password `password`

### Manual Configuration

1. Access Keycloak Admin Console: http://localhost:8080
2. Login with `admin` / `admin123`
3. Configure realm settings, clients, and users as needed
4. Update environment variables to match your configuration

### Client Configuration

The FastAPI client is configured with:
- **Client ID**: `fastapi-app`
- **Access Type**: Confidential
- **Direct Access Grants**: Enabled (for username/password login)
- **Service Accounts**: Enabled
- **Valid Redirect URIs**: `http://localhost:8000/*`

## Development

### Project Structure

```
authorization_types/
├── app/
│   ├── keycloak/           # Keycloak integration
│   ├── database/           # In-memory storage
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration
│   ├── models.py          # Data models
│   └── auth.py            # Legacy auth (minimal)
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docker-compose.yml     # Docker services
├── Dockerfile            # Application container
└── README.md
```

### Adding New Features

1. **New Endpoints**: Add to `app/main.py`
2. **Authentication**: Use `get_current_user_keycloak` dependency
3. **User Data**: Store/retrieve from local database
4. **Configuration**: Add to `app/config.py`
5. **Tests**: Add corresponding tests in `tests/`

## Troubleshooting

### Common Issues

1. **Keycloak Connection Error**
   ```bash
   # Check if Keycloak is running
   curl http://localhost:8080/health
   
   # Check container logs
   docker-compose logs keycloak
   ```

2. **Authentication Failures**
   - Verify client configuration in Keycloak
   - Check client secret matches environment variable
   - Ensure users exist and are enabled

3. **Token Validation Errors**
   - Check token expiration
   - Verify Keycloak realm and client settings
   - Ensure network connectivity to Keycloak

4. **Database Issues**
   - Memory is cleared on application restart
   - Check for memory usage in long-running applications
   - For production, use persistent database storage

### Getting Help

- Check application logs: `docker-compose logs app`
- Check Keycloak logs: `docker-compose logs keycloak`
- Verify configuration: Review environment variables
- Test endpoints: Use the interactive docs at `/docs`

## Migration from JWT

This project replaces a previous JWT-based authentication system with Keycloak integration. Key changes:

- **Removed**: Custom JWT token generation and validation
- **Removed**: Refresh token management
- **Added**: Keycloak OpenID Connect integration
- **Added**: Docker and docker-compose setup
- **Added**: Local database for user data
- **Improved**: Security through industry-standard authentication

The API endpoints remain largely the same for compatibility, but now use Keycloak for authentication instead of custom JWT tokens. 