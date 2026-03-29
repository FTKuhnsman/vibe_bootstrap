# Dependency Map

Reference for understanding what could break when changing a given file or component. Update when architecture changes significantly.

---

## Backend Dependency Graph

<!-- Document model relationships, FK chains, and service dependencies.
Example:
```
User
  +--< Event.created_by (FK)
  +--< Participant.user (FK)

Event
  +--< Module.event (FK)
```
-->

## Frontend Dependency Graph

<!-- Document core exports, shared state, and component dependencies.
Example:
- eventBus.ts → used by all module hooks
- AuthContext → wraps entire app
- moduleRegistry.ts → used by Canvas to render modules
-->

## Change Impact Matrix

<!-- When you change X, what else could break?
| Changed File | Impacts | Risk |
|-------------|---------|------|
| core/models.py | All modules (FK relationships) | High |
| auth context | Every authenticated component | High |
-->

## Cross-Module Communication

<!-- How modules communicate without direct imports.
- Event bus patterns
- Shared API utilities
- WebSocket channels
-->
