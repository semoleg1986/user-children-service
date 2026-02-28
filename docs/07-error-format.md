# Error Format — RFC 7807

## Purpose

Сервис использует единый формат ошибок на основе RFC 7807 (Problem Details for HTTP APIs).
Это обеспечивает согласованный контракт ошибок для web/mobile/admin клиентов.

---

## Response Shape

Все ошибки возвращаются как `application/problem+json` со следующими полями:

- `type`: строка‑идентификатор типа ошибки
- `title`: краткое название
- `status`: HTTP статус
- `detail`: подробное описание
- `instance`: путь/идентификатор запроса (опционально)

---

## Example

```json
{
  "type": "https://example.com/problems/access-denied",
  "title": "Access denied",
  "status": 403,
  "detail": "You cannot access this resource",
  "instance": "/v1/user/users/123/children"
}
```

---

## Standard Problem Types

- `https://example.com/problems/not-found` → 404
- `https://example.com/problems/access-denied` → 403
- `https://example.com/problems/validation` → 422
- `https://example.com/problems/conflict` → 409
- `https://example.com/problems/unauthorized` → 401

---

## Mapping from Application Errors

- `NotFoundError` → 404 / `not-found`
- `AccessDeniedError` → 403 / `access-denied`
- `InvariantViolationError` → 409 / `conflict`

---

## Notes

1. Для продакшена домен в `type` должен быть заменен на ваш реальный домен.
2. Клиенты должны использовать `type` для программной обработки ошибок.
