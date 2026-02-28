# Child Management Service — Domain Model

## Purpose

Фиксирует все агрегаты, сущности и value objects в системе.  
Служит **контрактом для реализации домена**, без привязки к инфраструктуре или интерфейсам.

---

## Aggregates

### 1. User (Aggregate Root)

- **Definition**: владелец детей, точка входа для всех изменений в агрегате.
- **Attributes**:
  - `user_id: UUID` — уникальный идентификатор
  - `name: str` — имя пользователя
  - `children: List[Child]` — коллекция детей
- **Behavior / Methods**:
  - `add_child(child_data)` — добавление ребенка
  - `archive_child(child_id)` — архивирование ребенка (soft-delete)
  - `restore_child(child_id)` — восстановление архивированного ребенка
  - `get_children()` — получить список детей
  - `get_child(child_id)` — получить ребёнка по id
  - `update_child(child_id, data)` — изменить данные ребенка
- **Invariants**:
  - Child не существует вне User
  - Child не может быть добавлен дважды
  - Все изменения проходят через User
- **Relationships**:
  - Owns 0..* Child
- **Notes**:
  - Aggregate Root обеспечивает целостность данных
  - Проверка доступа выполняется в **Application Layer** через Policies **до** вызова методов агрегата (Domain не содержит проверок ролей; см. 05, 06)
  - Создание User возможно как Admin'ом, так и самим пользователем (только для себя)

---

### 2. Child (Entity)

- **Definition**: сущность, принадлежащая User
- **Attributes**:
  - `child_id: UUID` — уникальный идентификатор
  - `name: str` — имя ребенка
  - `birthdate: date` — дата рождения
  - `status: active | archived` — состояние жизненного цикла Child
  - `stories: List[Story]` — истории ребенка
- **Behavior / Methods**:
  - `add_story(story_data)` — добавить историю
  - `get_stories()` — получить все истории
  - `archive()` — пометить Child как archived (soft-delete)
  - `restore()` — восстановить Child из archived
- **Relationships**:
  - Part of User aggregate
- **Invariants**:
  - Child существует только внутри User
  - Все изменения проходят через User
  - archived Child не возвращается в обычных пользовательских списках
- **Notes**:
  - Не имеет собственного жизненного цикла вне User
  - Value Objects могут использоваться для данных истории

---

### 3. Story (Value Object / Entity)

- **Definition**: запись / история ребенка
- **Attributes**:
  - `story_id: UUID`
  - `title: str`
  - `content: str`
  - `created_at: datetime`
- **Behavior / Methods**:
  - Immutable (Value Object), можно создавать и читать
  - Может быть расширен для добавления метаданных
- **Relationships**:
  - Belongs to Child
- **Invariants**:
  - Не может существовать без Child
- **Notes**:
  - Можно рассматривать как Value Object, если не требуется отдельный идентификатор

---

## Policies

- **Definition**: правила доступа к агрегатам
- **Responsibilities**:
  - Проверка прав User и Admin
  - Гарантия соблюдения инвариантов при операциях
- **Examples**:
  - `can_add_child(user, actor)` — только User или Admin через User
  - `can_archive_child(user, actor)` — нельзя архивировать чужих детей
  - `can_restore_child(user, actor)` — нельзя восстанавливать чужих детей
  - `can_view_children(user, actor)` — User видит своих, Admin видит всех
- **Location**: Domain Layer, без знаний об инфраструктуре

---

## Repositories (Interfaces)

- **UserRepository**
  - `get_by_id(user_id: UUID) -> User | None` — вернуть User или None, если не найден
  - `save(user: User)`
  - `delete(user_id: UUID)`
- **Notes**:
  - Domain не реализует сохранение
  - Infrastructure реализует через ORM
  - Работа только с агрегатом User
  - При отсутствии пользователя: возврат None или исключение — на усмотрение реализации (Application Layer должен обрабатывать оба варианта)

---

## Value Objects

- **ChildData**
  - Иммутабельный объект для создания Child (name, birthdate, опционально child_id)
  - Используется в `User.add_child(child_data)`
- **StoryData**
  - Иммутабельный объект для создания Story (title, content, опционально story_id)
  - Используется в `Child.add_story(story_data)`
- **Notes**:
  - Обеспечивают неизменность данных при передаче между слоями
  - Можно использовать для DTO внутри Domain Layer

---

## UML Reference

- **Aggregate Structure**:
```shell
User (Aggregate Root)
└── Child
└── Story (Value Object)
```

- **Relationships**:
  - User owns Child
  - Child contains Stories
  - Policies привязаны к User / Child, проверяют действия акторов

---

## Notes

1. Domain Layer **не зависит от Infrastructure**.
2. Все бизнес-инварианты закреплены в агрегатах.
3. Policies обеспечивают безопасность и целостность, не смешивая роли с сущностями.
4. Repository интерфейсы позволяют Infrastructure слой реализовать персистентность.
5. Любые новые сущности или value objects должны быть согласованы с этим документом и добавлены в UML.
