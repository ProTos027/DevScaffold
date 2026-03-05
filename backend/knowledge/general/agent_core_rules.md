# Agent Core Rules

## MANIFEST VERACITY (Hard Rule)
The `ProjectManifest` data and the framework documentation in this KB are the **Absolute Truth**. 
- **NEVER** hallucinate folder names or file extensions.
- **NEVER** use a framework version not explicitly supported (e.g., don't use Express 5 features if `package.json` says `^4.18`).
- **ALWAYS** scan the manifest for "hidden" dependencies (like `express-async-errors` or `pydantic-settings`) before writing core logic.

## BRIDGE VALIDATION CHECKLIST (Connectivity)
Rules for where layers connect (Frontend → Backend, Backend → DB).
1. **CORS**: **ALWAYS** match the backend's allowed origins to the frontend's `frontend_port` contract.
2. **Auth Headers**: **NEVER** omit `Bearer ` prefix if using JWT. **ALWAYS** use `Authorization` (uppercase A).
3. **Payload Parity**: If a contract says `id` (integer), **NEVER** send `uuid` (string).

## DEPRECATION & LEAK PREVENTION
Common "Cross-Stack" leaks and outdated patterns to avoid:
| Feature | **NEVER** (Outdated/Leak) | **ALWAYS** (Modern/Correct) |
| :--- | :--- | :--- |
| Pydantic | `.dict()` / `.from_orm()` | `.model_dump()` / `.model_validate()` |
| Time | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| JSON Response | `res.send()` / `res.write()` | `res.json()` |
| Logic Location | Business logic in View/Controller | Business logic in **Service** layer |
| Path Params | `/items?id=123` (for lookup) | `/items/{id}` (RESTful) |

## BAN "LOGICAL SHORTHAND"
- **NEVER** assume `request.user` or `Principal` is an ID. 
- **ALWAYS** explicitly extract the identifier (e.g., `user_id = payload.get("id")`) and convert type if necessary.
- **NEVER** assume a framework "automagically" handles ownership. **ALWAYS** write an explicit `if (resource.owner_id !== user.id)` check.
