Домашнее задание №5  
Тема: «JWT-авторизация с refresh-токенами в FastAPI»  

-------------------------------------------------------------------
## Task 1 — Выдача пары токенов  
• Цель: разделить краткий access-token и долгий refresh-token.  
• Шаги:  
  – Эндпоинт `/login` возвращает пару: `access_token` (HS256, `exp = 15 мин`) и `refresh_token` (HS256, `exp = 7 дней`).  
  – В `refresh_token` включить `jti` (UUID) и `sub`.  
  – Сохранить `jti` в `refresh_store: dict[jti → {"username", "expires_at"}]`.

## Task 2 — Обновление access-токена  
• Цель: обменять refresh-token на новый access-token.  
• Шаги:  
  – Эндпоинт `/token/refresh` принимает refresh-token.  
  – Проверяет подпись, `exp` и наличие `jti` в `refresh_store`.  
  – Выдаёт новый access-token (15 мин) и **повторно** тот же refresh-token (если ротация отключена).

## Task 3 — Ротация и Blacklist  
• Цель: реализовать скользящие сессии.  
• Шаги:  
  – `.env`: `ROTATE_REFRESH = true/false`.  
  – Если включено, `/token/refresh` генерирует новый refresh-token с новым `jti`, а старый добавляет в `blacklist_refresh: set[str]`.  
  – При валидации refresh-token проверять отсутствие `jti` в blacklist.

## Task 4 — «Remember me» TTL  
• Цель: разная длительность refresh-токена.  
• Шаги:  
  – Расширить `LoginRequest` полем `remember_me: bool = False`.  
  – Если `remember_me`, `exp(refresh)` = 30 дней, иначе 7 дней.  
  – Access-token всегда 15 мин (параметризовать в settings).

## Task 5 — In-memory Users DB + хеш-пароли  
• Цель: хранить пользователей и их роли без внешних БД.  
• Шаги:  
  – `users_db = {username: {"password_hash": str, "roles": list[str]}}`.  
  – Хэшировать пароли `passlib.hash.sha256_crypt`.  
  – При логине / регистрации включать `roles` в payload обоих токенов.

## Task 6 — RBAC: проверка ролей и разграничение доступа  
• Цель: освоить **Role-Based Access Control (RBAC)** — механизм авторизации, при котором права определяются ролями, а не конкретными пользователями.  
• Что нужно сделать и проверить:  
  1. Создать зависимость `require_role(*allowed_roles)` — декоратор/функция-dependency, которая:  
     • Декодирует access-token,  
     • Извлекает список `roles` из payload,  
     • Проверяет, что любая из `allowed_roles` присутствует.  
     • При отсутствии роли возвращает HTTP 403 **Forbidden**.  
  2. Добавить примеры эндпоинтов:  
     – `/admin` → доступ только `admin`-ролям.  
     – `/manager` → доступ `admin` и `manager`.  
  3. В тестах показать отличие **аутентификации** (проверка токена) и **авторизации** (проверка ролей).  
     • Запрос без токена → 401 **Unauthorized**.  
     • С токеном, но без нужной роли → 403 **Forbidden**.  
     • С корректной ролью → 200.

## Task 7 — Регистрация + немедленная пара токенов  
• Цель: публичная ручка `/register` сразу возвращает access + refresh-токены.  
• Шаги:  
  – Проверять уникальность, хешировать пароль, принимать список ролей.  
  – Выдавать пару токенов с учётом `remember_me`.

## Task 8 — Тестирование (pytest + httpx + freezegun)  
1. Регистрация возвращает валидные access + refresh.  
2. `/token/refresh` выдаёт новый access (без ротации).  
3. Ротация: старый refresh в blacklist, новый работает.  
4. Просроченный refresh → 401.  
5. Logout отзывает refresh.  
6. RBAC: `/admin` → 200 c ролью, 403 без роли, 401 без токена.  
7. Remember-me → refresh живёт > 7 дней.  
8. Blacklisted refresh не работает.
