Домашние задания для освоения темы базовой авторизации в FastAPI на репозитории `authorization_types`.

-------------------------------------------------------------------
# TASK-SET: Basic Auth Hands-On

## Task 1 — Перенос учётных данных в переменные окружения
• Цель: убрать хардкод из `auth.py`, научиться работать с `.env`.  
• Файлы:  
  – `authorization_types/app/config.py`: добавить поля `API_USERNAME`, `API_PASSWORD`.  
  – `authorization_types/app/auth.py`: заменить локальные `USERNAME`, `PASSWORD` на импорт из `settings`.  
  – `.env.example` (новый): шаблон с переменными `API_USERNAME`, `API_PASSWORD`.

## Task 2 — Захешированные пароли
• Цель: внедрить безопасное хранение паролей.  
• Библиотека: `passlib`.  
• Файлы:  
  – `pyproject.toml`: добавить зависимость.  
  – `authorization_types/app/auth.py`:  
      1. Импортировать `sha256_crypt` из `passlib.hash`.  
      2. Заменить сравнение plain-text на проверку хеша из `API_PASSWORD_HASH`.  
  – `.env.example`: добавить `API_PASSWORD_HASH`; оставить заметку по генерации.

## Task 3 — Поддержка нескольких пользователей (словарь)
• Цель: хранить пользователей в памяти и проверять авторизацию против словаря.  
• Файлы:  
  – `authorization_types/app/auth.py`:  
      1. Создать глобальный словарь `USER_DB: dict[str, str]`, где ключ — username, значение — bcrypt-хеш пароля.  
      2. Проверять креденшалы в зависимости `get_current_user` через `USER_DB`.  
  – `.env.example`: добавить примеры нескольких пользователей и инструкцию по расширению словаря.

## Task 4 — Пример защищённого POST и публичного GET
• Цель: отработать зависимость `get_current_user` на практике.  
• Файлы:  
  – `authorization_types/app/main.py`:  
      1. Создать in-memory список `objects_db: list[dict]`.  
      2. POST `/objects` (защищённый): принимает `{"data": str}`, добавляет `{"data": ..., "author": current_user}` в `objects_db` и возвращает объект.  
      3. GET `/objects` (публичный): возвращает содержимое `objects_db`.
## Task 5 — Тесты
• Цель: закрепить навыки тестирования.  
• Файлы:  
  – `authorization_types/tests/test_auth_handlers.py`:  
      1. Публичный эндпоинт `/public` — 200.  
      2. POST `/objects` без заголовка — 401.  
      3. POST `/objects` с неверными учетными данными — 401.  
      4. POST `/objects` с валидными данными — 200 и в ответе присутствует `author`.  
      5. GET `/objects` — 200 и список содержит ранее созданный объект.

