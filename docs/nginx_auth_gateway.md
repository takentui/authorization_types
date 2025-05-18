# Nginx Basic Authentication Gateway

This document explains how to use Nginx as a centralized authentication gateway for multiple microservices.

## Architecture Overview

```
                     ┌─────────────────────────────────────────┐
                     │                                         │
                     │             NGINX GATEWAY               │
                     │                                         │
                     │  ┌─────────────┐                        │
  Client Request     │  │             │    Basic Auth Check    │
 ─────────────────▶  │  │Load Balancer│─────────────────────┐  │
                     │  │             │                     │  │
                     │  └─────────────┘                     ▼  │
                     │          │                   ┌───────────────┐
                     │          │                   │  Auth Module  │
                     │          │                   │  (.htpasswd)  │
                     │     public handler           └───────────────┘
                     │          │                           │  │
                     │          │      If Authenticated     │  │
                     │          ◀───────────────────────────┘  │
                     │          │                              │
                     └──────────┼──────────────────────────────┘
                                │                             │
                                ▼                             ▼
                     ┌─────────────────────┐      ┌─────────────────────┐
                     │                     │      │                     │
                     │   Microservice A    │      │   Microservice B    │
                     │                     │      │                     │
                     └─────────────────────┘      └─────────────────────┘
```

## How It Works

1. All client requests go to the Nginx gateway first
2. Nginx authenticates the request using basic authentication
3. If authenticated, Nginx forwards the request to the appropriate backend service
4. Backend services don't need to implement authentication logic
5. Different authentication rules can be applied to different service paths

## Benefits of Centralized Authentication

- **Single authentication point**: Manage all credentials in one place
- **Consistent security**: Apply the same authentication rules across services
- **Reduced implementation complexity**: Backend services focus on business logic
- **Performance**: Authentication at the web server level is faster than application-level auth
- **Unified logging**: Authentication events are logged in a single place

## Nginx Configuration

### Basic Configuration Template

```nginx
# In /etc/nginx/nginx.conf or equivalent

http {
    # Define upstream servers (backend services)
    upstream service_a {
        server service-a:8000;
        # Add more instances for load balancing if needed
        # server service-a-2:8000;
    }

    upstream service_b {
        server service-b:8000;
    }

    # Main server configuration
    server {
        listen 80;
        server_name example.com;

        # Redirect HTTP to HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name example.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Global authentication for all services
        auth_basic "Restricted Area";
        auth_basic_user_file /etc/nginx/.htpasswd;

        # Service A
        location /service-a/ {
            # For specific service credentials, you can override auth here
            # auth_basic "Service A";
            # auth_basic_user_file /etc/nginx/.htpasswd-service-a;
            
            proxy_pass http://service_a/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Pass authentication information to the backend if needed
            proxy_set_header Authorization $http_authorization;
        }

        # Service B
        location /service-b/ {
            proxy_pass http://service_b/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Public endpoints (no authentication)
        location /public/ {
            auth_basic off;
            proxy_pass http://service_a/public/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Health check endpoints
        location /health/ {
            auth_basic off;
            proxy_pass http://service_a/health/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## Setting Up Basic Authentication

### Creating the Password File

1. Install `apache2-utils` (Debian/Ubuntu) or `httpd-tools` (CentOS/RHEL):

```bash
# Debian/Ubuntu
apt-get install apache2-utils

# CentOS/RHEL
yum install httpd-tools
```

2. Create a `.htpasswd` file:

```bash
# Create a new file with first user
htpasswd -c /etc/nginx/.htpasswd admin

# Add additional users (without -c flag which would overwrite the file)
htpasswd /etc/nginx/.htpasswd user2
```

3. Secure the file:

```bash
chmod 600 /etc/nginx/.htpasswd
chown nginx:nginx /etc/nginx/.htpasswd
```

### Docker Compose Setup

```yaml
version: '3'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/.htpasswd:/etc/nginx/.htpasswd
    networks:
      - app-network

  service-a:
    image: service-a-image
    networks:
      - app-network
    environment:
      - SERVICE_NAME=service-a

  service-b:
    image: service-b-image
    networks:
      - app-network
    environment:
      - SERVICE_NAME=service-b

networks:
  app-network:
    driver: bridge
```

## Advanced Configurations

### Different Authentication for Different Services

You can create multiple `.htpasswd` files to have different credentials for different services:

```nginx
# Admin service with stricter auth
location /admin/ {
    auth_basic "Admin Area";
    auth_basic_user_file /etc/nginx/.htpasswd-admin;
    proxy_pass http://admin_service/;
    # ...
}

# Public API with different auth
location /api/ {
    auth_basic "API Access";
    auth_basic_user_file /etc/nginx/.htpasswd-api;
    proxy_pass http://api_service/;
    # ...
}
```

### Combining with IP Restrictions

Restrict access based on both basic auth and IP addresses:

```nginx
location /admin/ {
    # Allow only specific IPs
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    # And require authentication
    auth_basic "Admin Area";
    auth_basic_user_file /etc/nginx/.htpasswd-admin;
    
    proxy_pass http://admin_service/;
    # ...
}
```

### Enhanced Security with Rate Limiting

Protect against brute force attacks:

```nginx
# Define a limit zone
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=1r/s;

server {
    # Other configurations...
    
    location /admin/ {
        # Apply rate limiting
        limit_req zone=auth_limit burst=5 nodelay;
        
        auth_basic "Admin Area";
        auth_basic_user_file /etc/nginx/.htpasswd-admin;
        
        proxy_pass http://admin_service/;
        # ...
    }
}
```

## Passing Authentication to Backend Services

If your backend services need the authenticated username, you can pass it:

```nginx
location /api/ {
    auth_basic "API Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Pass the authenticated user as a header
    proxy_set_header X-Authenticated-User $remote_user;
    
    proxy_pass http://api_service/;
    # ...
}
```

## Security Best Practices

1. **Always use HTTPS**: Basic authentication sends credentials encoded, not encrypted
2. **Use strong passwords**: Enforce password complexity for all `.htpasswd` entries
3. **Separate user groups**: Create different `.htpasswd` files for different access levels
4. **Implement rate limiting**: Protect against brute force attacks
5. **Regularly rotate credentials**: Change passwords periodically
6. **Use least privilege principle**: Give users access only to what they need
7. **Backup authentication files**: Keep secure backups of your `.htpasswd` files
8. **Monitor and log**: Keep detailed logs of authentication attempts

## Limitations and Considerations

- Basic authentication is simple but lacks advanced features like token expiration
- For production environments with many users, consider alternatives like OAuth2
- Basic auth can't provide fine-grained authorization at the API endpoint level
- Session management must be handled by the backend services if needed

## Expanding to Advanced Authentication Methods

For more complex needs, Nginx Plus supports:
- JWT validation
- OAuth 2.0 authentication
- OpenID Connect

For open-source Nginx, you can also implement these using Lua modules like `lua-resty-openidc`.

---

# Шлюз аутентификации Nginx

Этот документ объясняет, как использовать Nginx в качестве централизованного шлюза аутентификации для нескольких микросервисов.

## Обзор архитектуры

```
                     ┌─────────────────────────────────────────┐
                     │                                         │
                     │             NGINX ШЛЮЗ                  │
                     │                                         │
                     │  ┌─────────────┐                        │
  Запрос клиента     │  │             │ Проверка аутентификации│
 ─────────────────▶  │  │Балансировщик│─────────────────────┐  │
                     │  │             │                     │  │
                     │  └─────────────┘                     ▼  │
                     │          │                   ┌───────────────┐
                     │          │                   │ Модуль аутент.│
                     │          │                   │  (.htpasswd)  │
                     │     Публичные ручки          └───────────────┘
                     │          │                           │  │
                     │          │     Если аутентифицирован │  │
                     │          ◀───────────────────────────┘  │
                     │          │                              │
                     └──────────┼──────────────────────────────┘
                                ┼─────────────────────────────┐
                                ▼                             ▼
                     ┌─────────────────────┐      ┌─────────────────────┐
                     │                     │      │                     │
                     │   Микросервис A     │      │   Микросервис B     │
                     │                     │      │                     │
                     └─────────────────────┘      └─────────────────────┘
```

## Как это работает

1. Все запросы клиентов сначала проходят через шлюз Nginx
2. Nginx аутентифицирует запрос с помощью базовой аутентификации
3. Если запрос аутентифицирован, Nginx перенаправляет его в соответствующий бэкенд-сервис
4. Бэкенд-сервисам не нужно реализовывать логику аутентификации
5. Различные правила аутентификации могут применяться к разным путям сервисов

## Преимущества централизованной аутентификации

- **Единая точка аутентификации**: Управление всеми учетными данными в одном месте
- **Согласованная безопасность**: Применение одинаковых правил аутентификации для всех сервисов
- **Сниженная сложность реализации**: Бэкенд-сервисы фокусируются на бизнес-логике
- **Производительность**: Аутентификация на уровне веб-сервера быстрее, чем на уровне приложения
- **Единое логирование**: События аутентификации регистрируются в одном месте

## Конфигурация Nginx

### Базовый шаблон конфигурации

```nginx
# В /etc/nginx/nginx.conf или эквивалентном файле

http {
    # Определяем upstream серверы (бэкенд-сервисы)
    upstream service_a {
        server service-a:8000;
        # Добавьте больше экземпляров для балансировки нагрузки, если нужно
        # server service-a-2:8000;
    }

    upstream service_b {
        server service-b:8000;
    }

    # Основная конфигурация сервера
    server {
        listen 80;
        server_name example.com;

        # Перенаправляем HTTP на HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name example.com;

        # SSL конфигурация
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # Глобальная аутентификация для всех сервисов
        auth_basic "Restricted Area";
        auth_basic_user_file /etc/nginx/.htpasswd;

        # Сервис A
        location /service-a/ {
            # Для специфичных учетных данных сервиса можно переопределить auth здесь
            # auth_basic "Сервис A";
            # auth_basic_user_file /etc/nginx/.htpasswd-service-a;
            
            proxy_pass http://service_a/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Передаем информацию об аутентификации в бэкенд, если нужно
            proxy_set_header Authorization $http_authorization;
        }

        # Сервис B
        location /service-b/ {
            proxy_pass http://service_b/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Публичные эндпоинты (без аутентификации)
        location /public/ {
            auth_basic off;
            proxy_pass http://service_a/public/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Эндпоинты проверки работоспособности
        location /health/ {
            auth_basic off;
            proxy_pass http://service_a/health/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

## Настройка базовой аутентификации

### Создание файла паролей

1. Установите `apache2-utils` (Debian/Ubuntu) или `httpd-tools` (CentOS/RHEL):

```bash
# Debian/Ubuntu
apt-get install apache2-utils

# CentOS/RHEL
yum install httpd-tools
```

2. Создайте файл `.htpasswd`:

```bash
# Создайте новый файл с первым пользователем
htpasswd -c /etc/nginx/.htpasswd admin

# Добавьте дополнительных пользователей (без флага -c, который перезаписал бы файл)
htpasswd /etc/nginx/.htpasswd user2
```

3. Защитите файл:

```bash
chmod 600 /etc/nginx/.htpasswd
chown nginx:nginx /etc/nginx/.htpasswd
```

### Настройка Docker Compose

```yaml
version: '3'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/.htpasswd:/etc/nginx/.htpasswd
    networks:
      - app-network

  service-a:
    image: service-a-image
    networks:
      - app-network
    environment:
      - SERVICE_NAME=service-a

  service-b:
    image: service-b-image
    networks:
      - app-network
    environment:
      - SERVICE_NAME=service-b

networks:
  app-network:
    driver: bridge
```

## Расширенные конфигурации

### Разная аутентификация для разных сервисов

Вы можете создать несколько файлов `.htpasswd` для разных учетных данных для разных сервисов:

```nginx
# Админ-сервис с более строгой аутентификацией
location /admin/ {
    auth_basic "Административная зона";
    auth_basic_user_file /etc/nginx/.htpasswd-admin;
    proxy_pass http://admin_service/;
    # ...
}

# Публичный API с другой аутентификацией
location /api/ {
    auth_basic "API доступ";
    auth_basic_user_file /etc/nginx/.htpasswd-api;
    proxy_pass http://api_service/;
    # ...
}
```

### Комбинирование с ограничениями по IP

Ограничивайте доступ на основе как базовой аутентификации, так и IP-адресов:

```nginx
location /admin/ {
    # Разрешаем только определенные IP
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    # И требуем аутентификацию
    auth_basic "Административная зона";
    auth_basic_user_file /etc/nginx/.htpasswd-admin;
    
    proxy_pass http://admin_service/;
    # ...
}
```

### Усиленная безопасность с ограничением частоты запросов

Защита от брутфорс-атак:

```nginx
# Определяем зону ограничения
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=1r/s;

server {
    # Другие конфигурации...
    
    location /admin/ {
        # Применяем ограничение частоты запросов
        limit_req zone=auth_limit burst=5 nodelay;
        
        auth_basic "Административная зона";
        auth_basic_user_file /etc/nginx/.htpasswd-admin;
        
        proxy_pass http://admin_service/;
        # ...
    }
}
```

## Передача аутентификации бэкенд-сервисам

Если вашим бэкенд-сервисам нужно знать имя аутентифицированного пользователя, вы можете передать его:

```nginx
location /api/ {
    auth_basic "API доступ";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Передаем аутентифицированного пользователя в виде заголовка
    proxy_set_header X-Authenticated-User $remote_user;
    
    proxy_pass http://api_service/;
    # ...
}
```

## Лучшие практики безопасности

1. **Всегда используйте HTTPS**: Базовая аутентификация отправляет учетные данные в кодированном, но не зашифрованном виде
2. **Используйте сложные пароли**: Требуйте сложности паролей для всех записей в `.htpasswd`
3. **Разделяйте группы пользователей**: Создавайте разные файлы `.htpasswd` для разных уровней доступа
4. **Реализуйте ограничение частоты запросов**: Защитите от брутфорс-атак
5. **Регулярно меняйте учетные данные**: Периодически меняйте пароли
6. **Используйте принцип наименьших привилегий**: Давайте пользователям доступ только к тому, что им нужно
7. **Создавайте резервные копии файлов аутентификации**: Храните безопасные резервные копии ваших файлов `.htpasswd`
8. **Мониторинг и логирование**: Ведите подробные логи попыток аутентификации

## Ограничения и соображения

- Базовая аутентификация проста, но не имеет продвинутых функций, таких как истечение срока действия токена
- Для production-сред с большим количеством пользователей рассмотрите альтернативы, такие как OAuth2
- Базовая аутентификация не может обеспечить детальную авторизацию на уровне API-эндпоинтов
- Управление сессиями должно обрабатываться бэкенд-сервисами, если необходимо

## Расширение до продвинутых методов аутентификации

Для более сложных потребностей Nginx Plus поддерживает:
- Валидацию JWT
- Аутентификацию OAuth 2.0
- OpenID Connect

Для open-source Nginx вы также можете реализовать эти методы, используя Lua-модули, такие как `lua-resty-openidc`. 