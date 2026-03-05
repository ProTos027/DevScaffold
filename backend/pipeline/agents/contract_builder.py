"""
Contract Builder Agent - Generates Component Plan from Intent Spec.
"""
import json
from core.logger import get_logger
from ..utils.gemini import format_gemini_error, gemini_call_with_retry
from ..schemas import IntentSpecSchema, ComponentPlanSchema

logger = get_logger(__name__)


CONTRACT_BUILDER_SYSTEM_PROMPT = """You are a software architect for DevScaffold.
Convert a validated Intent Specification into a detailed Component Plan JSON.

── COMPONENT & DOMAIN RULES ──────────────────────────────────────────────────
- **`component_id`**: Use `snake_case` ONLY (e.g. `auth_domain`, `payment_gateway`).
- **Domain Scope**: A `Component` represents a logical **Bounded Domain** or **Zone** (e.g., 'User Management', 'Inventory System').
- **Grouping Rule**: Group ALL related modules (Controller/Service/Schema/Model) for a single domain into one `Component`.
- **Component Types**: 'backend_module' | 'frontend_component' | 'data_model' | 'middleware'
- **Middleware Rules**:
    - Use for cross-cutting logic (e.g. `auth_middleware`, `logging_interceptor`).
    - Define ownership clearly: middleware modifies req/res, it does not handle primary business logic.
- **Shared Utilities**: Create a `shared_utils` or `common` zone ONLY if the project requires cross-domain helpers (Logging, Config, DateUtils). Omit if the project is a trivial single-domain app.
- **`data_models`**: List exact entity names from the Intent Spec.
- **`public_interfaces`**: Transport-Agile formats:
    - `REST [METHOD] [PATH]` (e.g. `REST POST /api/v1/games`)
    - `WS [EVENT]` (e.g. `WS ON user_moved`)
    - `GRPC [SERVICE].[METHOD]` (e.g. `GRPC GameEngine.ProcessMove`)
- **`folder`**: State the relative root directory for the domain (e.g. "src/main/java/com/app/auth").
- **`files`**: List ALL files comprising this domain (e.g. ["AuthController.java", "AuthService.java", "User.java"]).

── DEPENDENCY & CIRCULAR DEPENDENCY RULES ───────────────────────────────────
- A component can only depend on other components declared in this same plan.
- Frontend MANDATORY LAYERED HIERARCHY:
    1. SHARED UI (e.g. Button, Modal): Atomic components with NO business logic and NO dependencies.
    2. CLIENTS (API_Client): Can depend on Shared UI. No dependency on contexts or pages.
    3. CONTEXTS (Auth_Context): Can depend on Clients and Shared UI.
    4. PAGES/COMPONENTS: Can depend on all of the above.
- NEVER make an API Client depend on a Context.

── DO NOT ───────────────────────────────────────────────────────────────────
- Do NOT rename entities from the Intent Spec (use exact names from `data_entities`).
- Do NOT create circular dependencies.
- Do NOT use vague responsibilities:
    - ❌ "handle user data"
    - ✅ "validate JWT, issue access/refresh tokens, revoke sessions"

── INJECTED CONTEXT (MANDATORY) ─────────────────────────────────────────────
The following sections will appear below this prompt. Treat ALL of them as hard constraints:
- "## PROJECT TIMELINE": Decisions made by upstream agents. Do not contradict them.
- "FRAMEWORK & PROJECT CONTEXT": Standards from the knowledge base. Follow strictly.
- "## PROJECT MANIFEST": The single source of truth for entity names, stack, and features. All component IDs, data_models, and public_interfaces MUST align with the Manifest exactly.
"""


def build_component_plan(
    spec: IntentSpecSchema,
    model_name: str,
    rag_service=None,
    manifest=None,
    on_exhaustion=None,
    action_history: str = ""
) -> ComponentPlanSchema:
    """
    Use Google GenAI SDK to generate Component Plan from Intent Spec.
    """
    if not model_name.startswith("gemini-"):
        logger.warning(f"Invalid model_name '{model_name}'. Falling back to 'gemini-2.5-flash'.")
        model_name = "gemini-2.5-flash"
        
    spec_json = spec.model_dump_json(indent=2)

    # ── RAG: retrieve framework conventions + prior spec context ──────────────
    rag_context = ""
    if rag_service:
        try:
            backend = spec.stack.backend.framework
            query = f"{backend} component plan architecture backend modules data models"
            rag_context = rag_service.retrieve(query, top_k=5)
        except Exception as e:
            logger.warning(f"RAG retrieval in contract_builder failed (non-fatal): {e}")

    system_instruction = CONTRACT_BUILDER_SYSTEM_PROMPT
    
    # ── Inject Action History (Narrative Context) ───────────────────────────
    if action_history:
        system_instruction += f"\n\n{action_history}"

    if rag_context:
        system_instruction += f"\n\nFRAMEWORK & PROJECT CONTEXT:\n{rag_context}"

    # Also inject manifest spec block so component plan references correct entity fields
    if manifest:
        manifest_block = manifest.get_prompt_block()
        if manifest_block:
            system_instruction += f"\n\n{manifest_block}"

    try:
        response = gemini_call_with_retry(
            model_name,
            contents=f"Intent Spec:\n{spec_json}\n\nGenerate the Component Plan:",
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_json_schema": ComponentPlanSchema.model_json_schema(),
            },
            on_exhaustion=on_exhaustion
        )
        
        content = response.candidates[0].content.parts[0].text
        plan_dict = json.loads(content)
        
        if isinstance(plan_dict, list):
            plan_dict = {"components": plan_dict}
        
        plan = ComponentPlanSchema(**plan_dict)

        # ── Register component plan into manifest ─────────────────────────────
        if manifest:
            try:
                manifest.register_component_plan(plan)
                logger.info(f"Manifest: component plan registered ({len(plan.components)} components)")
            except Exception as e:
                logger.warning(f"Manifest component plan registration failed (non-fatal): {e}")

        return plan
        
    except Exception as e:
        clean_msg = format_gemini_error(e)
        logger.error(f"CONTRACT BUILDER ERROR: {clean_msg}")
        raise ValueError(clean_msg)
