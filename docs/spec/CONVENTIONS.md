# Code Conventions

> Run `/spec conventions` to populate this file. Claude will read your code patterns and ask about preferences.

## Naming Conventions

<!-- Naming rules. Example:
| Element | Convention | Example |
|---------|-----------|---------|
| Python functions | snake_case | `get_user_events()` |
| Python classes | PascalCase | `EventSerializer` |
| React components | PascalCase | `ExpenseCard.tsx` |
| TypeScript functions | camelCase | `fetchItems()` |
| CSS classes | Tailwind utility-first | `className="flex gap-2"` |
| API endpoints | kebab-case or snake_case | `/api/calendar/items/` |
-->

## Error Handling Patterns

<!-- How errors are handled. Example:
- Backend: Let framework handle validation errors (400), raise explicit errors for 404
- Frontend hooks: Catch errors, set error state, surface to UI
- Never silently swallow errors — always log or display
- API errors return `{ "detail": "message" }` format
-->

## Validation Patterns

<!-- Input validation approach. Example:
- Backend: Serializer validation (validate_<field>, validate method)
- Frontend: Form validation before submission
- API boundary is the primary validation layer
-->

## Logging Standards

<!-- Logging approach. Example:
- Backend: Python logging module, structured logs
- Frontend: console.error for errors only, no console.log in production
- Log levels: ERROR (broken), WARNING (degraded), INFO (lifecycle)
-->

## Testing Patterns

<!-- Testing conventions. Example:
- Backend: pytest with test client, factory fixtures
- Frontend: Vitest + React Testing Library
- Test files: co-located or in tests/ subdirectory
- Fixtures: Factory functions, not static data
- Mocking: Mock external services, not internal modules
- Minimum: happy path + error case + edge case per component
-->

## Code Organization

<!-- Import ordering, module structure. Example:
- Python imports: stdlib → third-party → local
- TypeScript imports: react → libraries → local
- One component per file (React)
- Barrel exports (index.ts) for module public API
-->

## Security Conventions

<!-- Security patterns. Example:
- Never trust client input — validate at API boundary
- Use parameterized queries (ORM)
- Escape user content (framework handles)
- Auth required on all API endpoints by default
- Secrets in environment variables, never in code
-->

## Performance Patterns

<!-- Performance conventions. Example:
- Use select_related/prefetch_related for related queries
- Paginate all list endpoints
- React.memo for expensive components
- Lazy load routes and heavy components
-->
