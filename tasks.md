Домашнее задание №6  
Тема: «OAuth 2.0 авторизация в FastAPI (упрощённая практика)»  

-------------------------------------------------------------------

## Task 1 — Добавить второй OAuth-провайдер  
• Шаги:  
  – Выбрать любой публичный провайдер (Google, Discord, VK, Yandex).  
  – Добавить переменные окружения `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI` для нового провайдера.  
  – Реализовать `/login/<provider>` (redirect) и `/auth/callback/<provider>` (callback).  
  – Получать `access_token` провайдера и забирать минимальный профиль (`id`, `email`).  
  – На callback выдавать наш JWT (`user_id` + `email_verified`).

## Task 2 — Простая in-memory Users DB  
• Структура: `users_db = {provider_user_id: {"user_id": UUID, "email_verified": bool}}`.  
• При первом логине создаётся новая запись (генерируем `user_id`).  
• При повторном логине того же `provider_user_id` возвращаем существующий `user_id`.

## Task 3 — Проверка верифицированного email  
• Если провайдер возвращает `email_verified` (Google) — сохраняем флаг.  
• Декоратор `require_verified_email` → 403, если флаг False.  
• Пример защищённого эндпоинта `/private-data`.

## Task 4 — Тестирование (pytest + aioresponses)  
1. Первый логин нового пользователя создаёт запись.  
2. Повторный логин возвращает тот же `user_id`.  
3. `require_verified_email` блокирует доступ без верификации.  
4. Доступ разрешён при `email_verified=True`.
