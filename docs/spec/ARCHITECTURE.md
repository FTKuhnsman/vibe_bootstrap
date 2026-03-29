# Architecture Specification

> Run `/spec architecture` to populate this file. Claude will scan your codebase structure and ask about design decisions.

## System Overview

<!-- High-level architecture. Include a diagram if helpful. Example:
- Monorepo with separate backend/ and frontend/ directories
- Backend serves REST API, frontend is a SPA
- WebSocket layer for real-time updates
-->

## Directory Structure

<!-- Key directories and their purposes. Example:
```
project/
├── backend/
│   ├── core/           # Shared models, auth, base classes
│   ├── modules/        # Feature modules
│   └── config/         # Settings, URLs
├── frontend/
│   ├── src/
│   │   ├── core/       # Shell, routing, auth
│   │   ├── modules/    # Feature modules
│   │   └── shared/     # Reusable components
│   └── vite.config.ts
└── docs/
```
-->

## Data Flow

<!-- Request lifecycle from user action to database and back. Example:
1. User interacts with React component
2. Component calls custom hook
3. Hook calls API service (axios with auth interceptor)
4. REST Framework ViewSet processes request
5. ORM queries database
6. Serializer formats response
7. Response flows back through hook → component → UI
-->

## Authentication & Authorization

<!-- Auth mechanism, token flow, permission model. Example:
- Token-based auth (DRF TokenAuthentication)
- Login returns token, stored in localStorage
- All API requests include Authorization header
- Permission: IsAuthenticated + object-level filtering
-->

## State Management

<!-- How state is managed. Example:
- Local state: React useState per component
- Server state: Custom hooks with fetch-on-mount
- Global state: React Context for auth
- Real-time: Event bus for cross-component updates
-->

## Database Schema Overview

<!-- Key models and relationships. Example:
- User → Event (via Participant M2M)
- Event → Module (1:N)
- Module → Module-specific data (1:N)
-->

## Module/Component Boundaries

<!-- How the codebase is divided. Example:
- Each module is self-contained
- Modules never import from other modules — only from core/shared
- Cross-module communication via event bus or shared API
-->

## File Naming Conventions

<!-- How files are named. Example:
- Backend: snake_case.py (models.py, views.py, serializers.py)
- Frontend: PascalCase.tsx for components, camelCase.ts for utilities
- Tests: test_*.py (backend), *.test.ts(x) (frontend)
-->
