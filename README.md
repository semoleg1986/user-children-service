# user-children-service

Сервис домена `users / children / stories`.

## Что реализовано
### User API (`/v1/user`)
- `POST /users` — self-create профиля пользователя
- `GET /users/{user_id}/children`
- `POST /users/{user_id}/children`
- `PATCH /users/{user_id}/children/{child_id}`
- `DELETE /users/{user_id}/children/{child_id}` — soft-delete (archive)
- `POST /users/{user_id}/children/{child_id}/restore`
- `POST /users/{user_id}/children/{child_id}/stories`

### Admin API (`/v1/admin`)
- `POST /users`
- `GET /users`
- `GET /users/{user_id}/children`
- `GET /audit/events`

## Быстрый запуск
```bash
cd /Users/olegsemenov/Programming/monitoring/user-children-service
make install
make run
```

## JWT ожидания
- `sub` -> `user_id`
- `roles` -> роли (в т.ч. `admin`)
- `iss`, `aud`, `exp`
- верификация по `AUTH_JWKS_URL`

## Контракт
- OpenAPI: `/Users/olegsemenov/Programming/monitoring/user-children-service/openapi.yaml`
- Проверка контракта:
```bash
make openapi-check
make contract-provider
```

## Статус
Подтвержден в e2e smoke (`5/5`):
- register -> create profile -> add child
- admin users/children view
- audit feed доступен в admin-web
