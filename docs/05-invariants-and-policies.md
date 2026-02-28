# Child Management Service — Invariants and Policies

## Purpose

Фиксирует все бизнес-инварианты и политики доступа для Child Management Service.  
Обеспечивает **целостность агрегатов, безопасность действий акторов** и единообразное поведение системы.

---

## 1️⃣ Business Invariants

### 1. User → Child

- **Invariant 1**: Child существует только внутри User.
- **Invariant 2**: Child не может быть добавлен дважды с одинаковым `child_id`.
- **Invariant 3**: Все операции над Child (add, remove, update) проходят через User.
- **Invariant 4**: User Aggregate Root гарантирует целостность данных всех своих Child.
- **Invariant 5**: Child в пользовательских сценариях не удаляется физически, а переводится в состояние `archived` (soft-delete).
- **Invariant 6**: Архивированный Child не возвращается в стандартных списках детей.

### 2. Child → Story

- **Invariant 7**: Story принадлежит только одному Child.
- **Invariant 8**: Story immutable после создания (Value Object). Можно только добавлять новые.
- **Invariant 9**: Child не может содержать Story с дублирующимся `story_id`.

### 3. Admin / User Rules

- **Invariant 10**: Admin не владеет Child напрямую, действует через User.
- **Invariant 11**: User не может управлять чужими Child.
- **Invariant 12**: Любая попытка изменения Child / Story проверяется через Policies.
- **Invariant 13**: Политики должны применяться до изменения агрегата, предотвращая нарушение инвариантов.

---

## 2️⃣ Policies (Access Rules)

### 2.1 Admin Policies

| Policy            | Description                                  | Actor | Enforcement Point                                           |
|-------------------|----------------------------------------------|-------|-------------------------------------------------------------|
| can_view_user     | Admin может просматривать любого User        | Admin | Application Layer (вызов до доступа к агрегату)             |
| can_manage_user   | Admin может создавать/деактивировать любого User; User — только себя | Admin, User | Application Layer |
| can_view_children | Admin может просматривать детей любого User  | Admin | Application Layer (Policy из Domain, вызов в Application)   |
| can_update_child  | Admin может изменять Child только через User | Admin | Application Layer (та же политика, что и для User; см. 2.2) |

### 2.2 User Policies

| Policy            | Description                                                       | Actor       | Enforcement Point                                               |
|-------------------|-------------------------------------------------------------------|-------------|-----------------------------------------------------------------|
| can_add_child     | User может добавить нового Child только себе; Admin — любому User | User, Admin | Application Layer (Policy вызывается до вызова метода агрегата) |
| can_archive_child | User может архивировать только своего Child; Admin — любого       | User, Admin | Application Layer                                               |
| can_restore_child | User может восстанавливать только своего Child; Admin — любого    | User, Admin | Application Layer                                               |
| can_update_child  | User может изменить только своего Child; Admin — любого           | User, Admin | Application Layer                                               |
| can_view_children | User видит только своих Child; Admin — всех                       | User, Admin | Application Layer                                               |
| can_add_story     | User может добавить Story только своему Child; Admin — любому     | User, Admin | Application Layer                                               |

**Enforcement Point:** все политики **определены** в Domain Layer, но **вызываются** в Application Layer перед изменением или чтением агрегата. Domain Entities не содержат проверок доступа.

### 2.3 General / Supporting Policies

- `is_authenticated(actor)` — проверка идентификации через AuthService
- `is_authorized(actor, action, target)` — проверка, что actor имеет право выполнить действие над target
- `check_invariants(aggregate)` — проверка всех бизнес-инвариантов перед commit через UnitOfWork

---

## 3️⃣ Enforcement Strategy

1. **Application Layer**:
   - Проверка actor через AuthService
   - Вызов Policy перед изменением агрегата
2. **Domain Layer**:
   - Методы User/Child применяют инварианты
   - Выбрасывают исключения при нарушении
3. **Infrastructure Layer**:
   - Repositories и UnitOfWork обеспечивают атомарность транзакций
   - Не меняют бизнес-логику
4. **Testing**:
   - Unit-тесты агрегатов проверяют инварианты
   - Integration-тесты проверяют совместное применение Policies и агрегатов

---

## 4️⃣ Notes

- Любые новые Use Cases или сущности требуют добавления соответствующих Policies и проверки инвариантов.
- Admin → User → Child — строго соблюдаем цепочку владения.
- Story как Value Object immutable, добавляется только через Child.
- Hard-delete Child не используется в пользовательском API; endpoint удаления трактуется как archive (soft-delete).
- Этот документ является **контрактом для всей системы**: Domain, Application, Infrastructure, Tests.
