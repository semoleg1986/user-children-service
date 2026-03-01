# ADR-0001: Bounded Context For User-Children Service

## Status
Accepted

## Date
2026-02-28

## Context
System contains multiple services (`auth`, `admin`, `notification`, BFFs).
This service must have clear ownership boundaries to avoid business-logic leakage and shared-database coupling.

## Decision
`user-children-service` owns only:
- `User` aggregate for this context
- `Child` entity lifecycle
- `Story` lifecycle
- domain policies related to these entities

This service does not own:
- token issuance / authentication flows
- admin orchestration use-cases spanning multiple services
- notification workflows

Integration rule:
- external services interact through API/events only
- direct DB access by external services is prohibited

## Consequences
- domain invariants remain centralized and consistent
- service can evolve independently
- API contracts become primary integration mechanism

