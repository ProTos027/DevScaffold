"""
Generation Engine - The unified agent that generates both infrastructure and project components.
"""
import json
from core.logger import get_logger
from ..utils.gemini import gemini_call_with_retry
from ..schemas import GeneratedFilesResponse, IntentSpecSchema

logger = get_logger(__name__)


GENERATION_ENGINE_SYSTEM_PROMPT = """You are a master software engineer for DevScaffold.
Your job is to generate specific files for a project based on the Manifest.

── OUTPUT CONTRACT ──────────────────────────────────────────────────────────
- Output ONLY valid JSON matching the GeneratedFilesResponse schema.
- ZERO PLACEHOLDERS: Generate complete, functional code. No "implement here" comments.
- Path format: Every path MUST match a Full Path listed in the MANDATORY DIRECTORY LAYOUT exactly.

── ENGINEERING RULES ────────────────────────────────────────────────────────
- COORDINATION: Every file must follow the Directory Layout in the Manifest EXACTLY.
- CONSISTENCY: Every import path must match the actual file paths in the Directory Layout.
- STACK COMPLIANCE: Use the exact frameworks, versions, and API types defined in the Manifest.
- INTERFACE ACCURACY: All API endpoints and data models must match the locked Scope Contracts.
- CONTRACTS: Populate `cross_layer_contracts` with all facts that downstream phases need (port, base URL, env var names, auth headers).

── ANTI-LAZINESS & ANTI-MINIFICATION (CRITICAL) ─────────────────────────────
- NEVER minify, compress or collapse code. Every statement on its own line with proper indentation.
- ZERO PLACEHOLDERS for structural code: imports, app setup, router wiring, DB connections MUST always be complete.
- NEVER use `// ... rest of code`, `/* implementation here */` or generic `TODO` comments.
- If token budget is tight: stub ONLY complex business logic with a DEVSCAFFOLD_STUB marker, NEVER structural code:
    def process_move(board, move):
        # DEVSCAFFOLD_STUB: implement move validation and board update
        raise NotImplementedError("DEVSCAFFOLD_STUB: implement chess move validation")
- Log stubbed functions in `implementation_notes["placeholders"]` as comma-separated list.
- Every function body must be fully implemented OR a proper DEVSCAFFOLD_STUB.

── DO NOT ───────────────────────────────────────────────────────────────────
- Do NOT abbreviate code or omit logic for brevity.
- Do NOT use different variable names or paths than those in the Manifest.
- Do NOT create files outside the defined Directory Layout.
- Do NOT generate Dockerfiles, docker-compose.yml, Nginx configs, or any shell/bash scripts (.sh, .bash).
- Do NOT regenerate files already listed in a previously completed generation phase.

── INJECTED CONTEXT (MANDATORY) ─────────────────────────────────────────────
The following sections will appear below. Treat them as hard constraints:
- "## PROJECT TIMELINE": Decisions made by previous generation phases. Follow them.
- "## PROJECT MANIFEST": The single Source of Truth (ASoT). This includes the Intent Spec, Architectural Plan, and Directory Layout.
- "CONTEXT FROM KNOWLEDGE BASE": Framework best practices and code standards.
"""

def _call_gemini_for_phase(
    phase_name: str,
    prompt: str,
    intent_spec: IntentSpecSchema,
    model_name: str,
    rag_service=None,
    manifest=None,
    on_exhaustion=None,
    action_history: str = ""
) -> GeneratedFilesResponse:
    """Helper to handle common Gemini call logic for generation phases.
    Returns: GeneratedFilesResponse object with files, notes, and contracts
    """
    if not model_name.startswith("gemini-"):
        logger.warning(f"Invalid model_name '{model_name}'. Falling back to 'gemini-2.5-flash'.")
        model_name = "gemini-2.5-flash"

    # RAG Retrieval
    rag_context = ""
    if rag_service:
        try:
            backend = intent_spec.stack.backend.framework
            frontend = intent_spec.stack.frontend.framework if intent_spec.stack.frontend else ''
            
            # Phase-aware RAG query
            if phase_name == 'backend':
                query = f"{backend} domain:dynamic project_context best practices implementation models services routers"
            elif phase_name == 'frontend':
                query = f"{frontend} domain:dynamic project_context best practices implementation components pages state management"
            else:
                query = f"{backend} {frontend} domain:dynamic project_context implementation best practices"
                
            rag_context = rag_service.retrieve(query, top_k=7) # Increased top_k to 7
        except Exception as e:
            logger.warning(f"RAG retrieval in {phase_name} phase failed (non-fatal): {e}")

    # Build System Instruction - ORDER MATTERS (Last is most prominent)
    manifest_block = manifest.get_prompt_block() if manifest else ""
    system_instruction = GENERATION_ENGINE_SYSTEM_PROMPT
    if action_history:
        system_instruction += f"\n\n{action_history}"
    if rag_context:
        system_instruction += f"\n\nCONTEXT FROM KNOWLEDGE BASE:\n{rag_context}"
    if manifest_block:
        system_instruction += f"\n\n{manifest_block}"

    # Call Gemini
    response = gemini_call_with_retry(
        model_name,
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_json_schema": GeneratedFilesResponse.model_json_schema(),
        },
        on_exhaustion=on_exhaustion
    )

    content = response.candidates[0].content.parts[0].text
    data = json.loads(content)
    parsed = GeneratedFilesResponse(**data)
    
    return parsed

def generate_backend(intent_spec, model_name, **kwargs) -> GeneratedFilesResponse:
    """PHASE 1: Core Logic. Generates models, services, and routers."""
    prompt = """PHASE: BACKEND GENERATION
Generate all backend implementation files (models, services, schemas, routers, dependencies, database config).

CORS (MANDATORY): Configure CORS middleware on app startup. 
  - ALLOWED ORIGINS: Predict the frontend's dev port based on its framework (e.g., 3000 for Next.js/React-CRA, 5173 for Vite/Vue/Svelte, 8080 for legacy Vue).
  - Include: `http://localhost:{port}`, `http://127.0.0.1:{port}` using that predicted port.
  - Allow methods: ["*"], Allow headers: ["*"], Allow credentials: True.

INTERFACE_CONTRACTS (SHAPES): **MANDATORY**. Populate this field with a detailed Markdown summary of your implementation:
  - List ALL data models/schemas with their exact field names and types.
  - List ALL API endpoints with their HTTP methods, request body shapes, and response shapes.
  - Use exact naming from your generated code.

CROSS_LAYER_CONTRACTS: **MANDATORY**. Populate the `cross_layer_contracts` object accurately:
  - `api_base_url`, `auth_token_field`, `auth_header_format`, `db_url_env_var`, `websocket_library`.
  - `frontend_port`: Include the predicted port you used for CORS here.

IMPLEMENTATION_NOTES: **MANDATORY**. Populate `implementation_notes` with:
  - `packages_used`: comma-separated list of EVERY external package/library imported in your files.
  - `port`: the server port (e.g. "3000", "8000").
  - `db_handler`: the database library used (e.g. "sqlalchemy", "prisma", "hibernate", "django.db").

SECURITY CHECKLIST (MANDATORY for backend):
  - Auth middleware: ALWAYS ensure errors are returned correctly to prevent process continuation or double-responses.
  - Protected routes: validate ownership before update/delete.
  - WebSocket: validate JWT token on connection.
  - Passwords: Use a secure, stack-appropriate hashing library (e.g. `passlib` for Python, `bcrypt` for Node), NEVER store plaintext.
"""
    return _call_gemini_for_phase("backend", prompt, intent_spec, model_name, **kwargs)

def generate_frontend(intent_spec, model_name, **kwargs) -> GeneratedFilesResponse:
    """PHASE 2: UI & Integration. Generates components, pages, and API clients."""
    prompt = """PHASE: FRONTEND GENERATION
Generate all frontend implementation files (components, pages, context, API clients).

INTERFACE_CONTRACTS / CROSS_LAYER_CONTRACTS: **OMIT**. You are a consumer of these fields from the Manifest, not a producer. Do NOT regenerate or modify them.

PORT ADHERENCE: Read the `frontend_port` from the Backend's `cross_layer_contracts` in the Manifest. You MUST configure your dev server / vite.config / next.config to run on this exact port.

IMPLEMENTATION_NOTES: **MANDATORY**. Populate `implementation_notes` with:
  - `packages_used`: comma-separated list of EVERY frontend package (e.g. npm/yarn) imported in your files.
  - `frontend_port`: your dev server port (MUST match the backend's contract).

In `implementation_notes`, include UI framework details and state management choices.
"""
    return _call_gemini_for_phase("frontend", prompt, intent_spec, model_name, **kwargs)

def generate_infrastructure(intent_spec, model_name, **kwargs) -> GeneratedFilesResponse:
    """PHASE 3: Configuration. Generates dependency manifests and root config files only."""
    prompt = """PHASE: INFRASTRUCTURE GENERATION
Generate ONLY the following project-wide configuration and dependency files:
- `requirements.txt` (backend Python dependencies with pinned versions from implementation_notes)
- `package.json` (frontend Node dependencies with pinned versions from implementation_notes)
- `.env.example` (all environment variables referenced across backend and frontend, with placeholder values)
- `.gitignore` (standard rules for the project's frameworks)
- `README.md` (setup and run instructions based on the actual generated structure)
- Framework DB config only if needed (e.g. `backend/alembic.ini` for SQLAlchemy migrations)

PATH FORMAT (CRITICAL): All file paths must be bare relative paths with NO leading slash.
  CORRECT: `README.md`, `backend/alembic.ini`, `.env.example`
  WRONG:   `/README.md`, `\\README.md`

INTERFACE_CONTRACTS / CROSS_LAYER_CONTRACTS: **OMIT**. Do not generate these.

IMPLEMENTATION_NOTES: **OMIT**. You only Read these from previous phases, you do not write new ones.

PACKAGES (CRITICAL):
  1. SCAN ALL GENERATED FILES in the PROJECT MANIFEST / TIMELINE.
  2. Identify EVERY external dependency actually imported in the source code.
  3. READ the `packages_used` lists provided in `implementation_notes` by previous phases.
  4. VERIFY the two lists match. If a package is imported in code but missing from `implementation_notes`, you MUST include it anyway.
  5. Output:
     - `requirements.txt`: All backend dependencies (convert to pip format).
     - `package.json`: All frontend dependencies (convert to npm format).

Do NOT guess packages. Use ONLY what is actually imported in the generated source code.

Read the PROJECT TIMELINE carefully — use the exact library names and versions declared by previous phases.
"""
    return _call_gemini_for_phase("infrastructure", prompt, intent_spec, model_name, **kwargs)
