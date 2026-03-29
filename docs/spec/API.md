# API Specification

> Run `/spec api` to populate this file. Claude will scan your route definitions and controllers.

## Base URL & Versioning

<!-- API base URL and versioning. Example:
- Base URL: `/api/`
- No version prefix in v1
-->

## Authentication Scheme

<!-- How API auth works. Example:
- Method: Token-based (Authorization: Token <key>)
- Login: POST /api/auth/login/ → returns { token, user }
- Register: POST /api/auth/register/ → returns { token, user }
- All other endpoints require authentication
-->

## Request/Response Format

<!-- Standard shapes. Example:
- Content-Type: application/json
- Successful list: `{ "count": N, "results": [...] }`
- Successful detail: `{ ...fields }`
- All timestamps in ISO 8601
-->

## Error Response Format

<!-- Error shapes. Example:
```json
{ "detail": "Human-readable error message" }
```
- 400: Validation errors `{ "field": ["error"] }`
- 401: Not authenticated
- 403: Permission denied
- 404: Not found
- 500: Server error (never expose internals)
-->

## Pagination Pattern

<!-- How lists are paginated. Example:
- Style: Page number pagination
- Default page size: 20
- Query params: `?page=2&page_size=50`
- Response: `{ "count": 100, "next": "url", "previous": "url", "results": [...] }`
-->

## Endpoint Naming Convention

<!-- URL pattern rules. Example:
- Pattern: `/api/{module}/{resource}/`
- List: GET `/api/calendar/items/`
- Detail: GET `/api/calendar/items/{id}/`
- Create: POST `/api/calendar/items/`
- Update: PUT/PATCH `/api/calendar/items/{id}/`
- Delete: DELETE `/api/calendar/items/{id}/`
- Custom actions: POST `/api/expenses/items/{id}/settle/`
-->

## Common Headers

<!-- Headers used. Example:
| Header | Value | When |
|--------|-------|------|
| Authorization | Token <key> | All authenticated requests |
| Content-Type | application/json | Requests with body |
| Accept | application/json | All requests |
-->

## Rate Limiting

<!-- Rate limiting (if any). Example:
- Not implemented in v1
-->

## Endpoint Inventory

<!-- Filled as endpoints are built.
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/register/ | Create account | No |
| POST | /api/auth/login/ | Get auth token | No |
-->
