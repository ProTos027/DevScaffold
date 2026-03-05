import json
from .schemas import IntentSpecSchema, ComponentPlanSchema, GeneratedFilesResponse
from core.logger import get_logger

logger = get_logger(__name__)

class ProjectManifest:
    """
    Structured, typed fact store for the current pipeline run.
    """

    def __init__(self):
        # The dynamic store for manifest segments
        self.data = {}

    # Lifecycle Registration
    def register_spec(self, intent_spec: IntentSpecSchema) -> None:
        """
        Step 1: Register full intent. 
        Stored as 'intent' for the Architect (Contract Builder) phase.
        We prune 'explanation' and 'vague_intent' for the prompt view later.
        """
        self.data['intent'] = intent_spec.model_dump(exclude_none=True)
        logger.info(" Manifest: Intent Spec registered.")

    def register_component_plan(self, component_plan: ComponentPlanSchema) -> None:
        """
        Step 2: Register Component Blueprint and PRUNE the Intent.
        Once the blueprint is established, the high-level intent (explanations, etc.) is removed.
        """
        # Store components (Technical Blueprint)
        self.data['components'] = [
            c.model_dump(exclude_none=True) for c in component_plan.components
        ]
        
        # PRUNE: Remove high-level intent to clear prompt space
        if 'intent' in self.data:
            intent = self.data.pop('intent')
            # Retain only the bare technical context
            context = {
                "stack": intent.get('stack'),
                "api_type": intent.get('api_type'),
                "auth_method": intent.get('auth_method'),
                "complexity": 'minimal'
            }
            # Invisibility: Only keep active technical facts
            self.data['context'] = {k: v for k, v in context.items() if v}
            logger.info(" Manifest: Component Plan registered. Intent pruned.")

    def register_generation_result(self, result: GeneratedFilesResponse) -> None:
        """
        Step 3: Accumulate Generation Facts.
        Stores the full GeneratedFilesResponse (excluding file contents) into 'generation_res'.
        Each phase call merges into the same key, updating contracts and notes cumulatively.
        """
        if not result:
            return

        res_dict = result.model_dump(exclude={'files'}, exclude_none=True)
        # Invisibility: strip empty collections
        clean_res = {k: v for k, v in res_dict.items() if v}

        if clean_res:
            self.data['generation_res'] = clean_res
            logger.info(" Manifest: Generation result registered.")

    def get_prompt_block(self) -> str:
        """
        Returns the Manifest as a clean, structured JSON block.
        The content reflects the current phase due to the sliding window pruning.
        """
        # Filter out empty segments for a cleaner prompt
        active_view = {k: v for k, v in self.data.items() if v}
        
        manifest_json = json.dumps(active_view, indent=2)
        
        return f"""
## PROJECT MANIFEST (ABSOLUTE SOURCE OF TRUTH)
> [!IMPORTANT]
> The following JSON contains the locked technical blueprint. 
> You MUST follow all naming, paths, and interface signatures exactly.

```json
{manifest_json}
```
"""
