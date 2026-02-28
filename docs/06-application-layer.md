# Child Management Service — Application Layer

## Purpose

Фиксирует реализацию всех Use Cases через **Application Layer**, связывая Domain, Policies и UnitOfWork.  
Обеспечивает:
- соблюдение бизнес-инвариантов,
- управление транзакциями,
- проверку доступа через Policies,
- интеграцию с инфраструктурой (Repository, UnitOfWork).

---

## Responsibilities

1. Оркестровка действий агрегатов (User → Child → Story).  
2. Проверка Policies перед любым изменением агрегата.  
3. Обеспечение атомарности через UnitOfWork.  
4. Служит точкой интеграции с Interface Layer (API / DTO).  
5. Не содержит бизнес-логику: она остаётся в Domain Layer.

---

## Use Cases Implementation

### 0️⃣ Create User

**Input:** `actor`, `user_id`, `name`  
**Steps:**
1. Проверить аутентификацию (`is_authenticated(actor)`).
2. Проверить authorization через Policy (`can_manage_user(actor, user_id)`).
3. Проверить, что User не существует.
4. Создать `User` и сохранить через `UnitOfWork.commit(user)`.

**Notes:**
- Admin может создавать любого User.
- User может создавать **только себя**.

### 1️⃣ Add Child

**Input:** `actor`, `user_id`, `child_data`  
**Steps:**
1. Проверить аутентификацию (`is_authenticated(actor)`).
2. Получить User через `UserRepository.get_by_id(user_id)`; если `None` — выбросить `NotFoundError` (или аналог).
3. Проверить authorization через Policy (`can_add_child(user, actor)`).
4. Вызвать `user.add_child(child_data)` в Domain.
5. Сохранить агрегат через `UnitOfWork.commit(user)`.

**Exceptions:**
- User не найден → `NotFoundError`
- Нарушение Policy → `AccessDeniedError`
- Child с дублирующимся `child_id` → `InvariantViolationError`

---

### 2️⃣ Archive Child (soft-delete)

**Input:** `actor`, `user_id`, `child_id`  
**Steps:**
1. Проверка аутентификации (`is_authenticated(actor)`).
2. Получить User через `UserRepository.get_by_id(user_id)`; если `None` — `NotFoundError`.
3. Проверка Policy (`can_archive_child(user, actor)`).
4. Вызвать `user.archive_child(child_id)`; Child переводится в состояние `archived`.
5. Commit через UnitOfWork.

**Exceptions:** аналогично Add Child; плюс нарушение бизнес-инвариантов перехода состояния.

---

### 3️⃣ Restore Child

**Input:** `actor`, `user_id`, `child_id`  
**Steps:**
1. Проверка аутентификации (`is_authenticated(actor)`).
2. Получить User через `UserRepository.get_by_id(user_id)`; если `None` — `NotFoundError`.
3. Проверка Policy (`can_restore_child(user, actor)`).
4. Вызвать `user.restore_child(child_id)`.
5. Commit через UnitOfWork.

---

### 4️⃣ Update Child

**Input:** `actor`, `user_id`, `child_id`, `update_data`  
**Steps:**
1. Получить User через `UserRepository.get_by_id(user_id)`; если `None` — `NotFoundError`.
2. Проверка Policy (`can_update_child(user, actor)`).
3. Вызвать `user.update_child(child_id, update_data)`.
4. Commit через UnitOfWork.

---

### 5️⃣ Add Story

**Input:** `actor`, `user_id`, `child_id`, `story_data`  
**Steps:**
1. Получить User через `UserRepository.get_by_id(user_id)`; если `None` — `NotFoundError`.
2. Проверка Policy (`can_add_story(user, actor)`).
3. Получить Child через `user.get_child(child_id)`; если нет — ошибка (Child not found).
4. Вызвать `child.add_story(story_data)`.
5. Commit через UnitOfWork.

---

### 6️⃣ Admin Use Cases (например, View Children)

1. Получить User через `UserRepository.get_by_id(user_id)`; если `None` — `NotFoundError`.
2. Проверка Policy (`can_view_children(user, actor)`).
3. Вернуть агрегат или DTO.
- **Без изменения агрегата**, транзакции не нужны.

---

## Application Layer Structure

```shell
application/
├── init.py
├── use_cases/
│   ├── init.py
│   ├── add_child.py
│   ├── archive_child.py
│   ├── restore_child.py
│   ├── update_child.py
│   ├── add_story.py
│   └── view_children.py
├── services/
│   └── user_service.py   # агрегатные операции и orchestration
└── unit_of_work.py        # commit / rollback
```

- **Use Cases** вызываются через API Handlers в Interface Layer.  
- **Services** обеспечивают orchestration нескольких агрегатов.  
- **UnitOfWork** гарантирует атомарность.

---

## Rules & Constraints

1. **Domain Layer never contains access control.** Все проверки — через Policies.  
2. **UnitOfWork** обязателен для любых изменений агрегатов.  
3. **Repositories** используются только для загрузки/сохранения агрегатов.  
4. Все Use Cases должны быть покрыты unit-тестами.  
5. Application Layer может возвращать **DTO**, но не доменные объекты напрямую.

---

## Notes

- Любые новые сценарии добавляются через **новый use case + сервис**.  
- Интеграционные тесты проверяют правильность работы Policies + Domain + UnitOfWork.  
- Application Layer является **единственной точкой входа для изменений домена**.
- Публичный endpoint удаления Child (`DELETE`) может быть сохранен для совместимости, но семантика операции должна быть `archive`, не hard-delete.
- Ошибки API возвращаются в формате RFC 7807 (см. `docs/07-error-format.md`).
