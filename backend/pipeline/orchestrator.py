from .utils import gemini as utils
from core.logger import get_logger
from .rag_service import RAGService
from .schemas import IntentSpecSchema, CyclicDependencyError
from .rules import validate_intent_spec
from .utils.graph import sort_component_plan_in_place
from .action_logger import ActionLogger
from .project_manifest import ProjectManifest
from .rotation_manager import RotationManager
from assembly.builder import assemble_repository
from .agents.spec_builder import build_spec_from_prompt
from .agents.contract_builder import build_component_plan
from .agents.prompt_expander import expand_prompt_to_domain_knowledge
from .agents.generation_engine import generate_backend, generate_frontend, generate_infrastructure
from projects.models import Project, IntentSpec, ComponentPlan, ValidationError as ValidationErrorModel

logger = get_logger(__name__)


class PipelineOrchestrator:
    
    def __init__(self, project: Project):
        self.project = project
        self.user = project.user
        self.model_provider = project.model_provider
        self.api_key_obj = None
        self.action_logger = ActionLogger(project)
        
        self.api_key_obj = RotationManager.get_best_key(self.user, provider=self.model_provider)
        
        if self.api_key_obj:
            decrypted_key = self.api_key_obj.get_api_key()
            if not decrypted_key or not decrypted_key.strip():
                raise ValueError(f"API Key '{self.api_key_obj.name}' is empty or invalid. Please delete and re-add it.")
            
            utils.set_client(decrypted_key)
            logger.info(f"Auto-Rotation: Using API Key '{self.api_key_obj.name}'")
        else:
            from accounts.models import APIKey
            total_keys = APIKey.objects.filter(user=self.user, provider=self.model_provider).count()
            if total_keys > 0:
                raise ValueError(f"All {total_keys} keys for {self.model_provider} are currently exhausted or inactive. Please wait 24h or add a new key.")
            else:
                raise ValueError(f"No {self.model_provider} API key found. Please add one in the Secret Vault.")

    def _handle_exhaustion(self):
        """Mid-Run Rotation Handler — marks current key exhausted then rotates."""
        logger.warning(f"Mid-Run Exhaustion detected for '{self.api_key_obj.name}'. Rotating...")
        RotationManager.mark_exhausted(self.api_key_obj)
        key_obj = utils.rotate_client(self.user, self.model_provider)
        if key_obj:
            self.api_key_obj = key_obj

    def run(self, prompt: str = None) -> bool:
        """
        Run the complete pipeline.
        Returns True if successful, False otherwise.
        """
        try:
            target_prompt = self.project.prompt or prompt
            self.action_logger.clear()
            
            rag_service = RAGService()
            manifest = ProjectManifest()

            # Stage 1: Build or Load Intent Spec
            if hasattr(self.project, 'intent_spec') and (self.project.spec_confirmed or self.project.status == 'review_required'):
                self._update_status('spec_loading', 'Loading Intent Spec', 10)
                spec_model = self.project.intent_spec
                intent_spec = IntentSpecSchema(**spec_model.to_dict())
            else:
                self._update_status('spec_building', 'Building Intent Spec', 15)
                intent_spec = build_spec_from_prompt(
                    target_prompt,
                    self.project.gemini_model,
                    rag_service=rag_service,
                    on_exhaustion=self._handle_exhaustion
                )

            # Save Intent Spec (Essential: Save BEFORE validation so user sees what was parsed)
            spec_defaults = intent_spec.model_dump()
            spec_defaults['data_entities'] = [e.model_dump() for e in intent_spec.data_entities]
            
            spec_obj, created = IntentSpec.objects.update_or_create(
                project=self.project,
                defaults=spec_defaults
            )
            
            # Always pause if not confirmed
            if not self.project.spec_confirmed:
                self._update_status('review_required', 'Review Specification Required', 30)
                return True # Stop but not failed

            # ── [COMMITMENT] Finalize Architectural State ──────────────────
            manifest.register_spec(intent_spec)
            
            if rag_service:
                try:
                    # Load framework docs (Long-Term Framework Memory)
                    frameworks = [f for f in [
                        intent_spec.stack.backend.framework if intent_spec.stack.backend else None,
                        intent_spec.stack.frontend.framework if intent_spec.stack.frontend else None,
                    ] if f]
                    if frameworks:
                        rag_service.load(frameworks=frameworks)

                    # Expand user prompt into domain knowledge and inject into RAG
                    domain_knowledge = expand_prompt_to_domain_knowledge(
                        target_prompt,
                        self.project.gemini_model,
                        on_exhaustion=self._handle_exhaustion
                    )
                    if domain_knowledge:
                        rag_service.add_text(domain_knowledge, source='prompt_expansion')

                    logger.info(f" ASoT: Intent Spec committed to Manifest and RAG (frameworks + domain knowledge loaded)")
                except Exception as e:
                    logger.error(f" Architectural commitment failed: {e}")

            # Log spec building action (Only once confirmed)
            self.action_logger.log('spec_building', 'spec_builder', 'built_intent_spec', {
                "stack": intent_spec.stack.model_dump(),
                "api_type": intent_spec.api_type,
                "auth_method": intent_spec.auth_method,
                "creative_vision": intent_spec.creative_vision,
                "complexity": 'minimal'
            })
            is_valid, errors = validate_intent_spec(intent_spec)
            
            if not is_valid:
                # Clear old validation errors
                ValidationErrorModel.objects.filter(project=self.project).delete()
                
                # Save new validation errors
                for error in errors:
                    ValidationErrorModel.objects.create(
                        project=self.project,
                        rule_name=error.split(':')[0],
                        error_message=error,
                        severity='error'
                    )
                self.project.mark_failed(f"Validation failed: {'; '.join(errors)}")
                return False
            
            # Clear any previous validation errors if now valid
            ValidationErrorModel.objects.filter(project=self.project).delete()
            
            self.action_logger.log('validating', 'validator', 'validation_passed', {
                'rules_checked': len(errors)
            })
            
            # Stage 3: Build Component Plan
            self._update_status('planning', 'Building Component Plan', 40)
            component_plan = build_component_plan(
                intent_spec,
                self.project.gemini_model,
                rag_service=rag_service,
                manifest=manifest,
                on_exhaustion=self._handle_exhaustion,
                action_history=self.action_logger.get_summary()
            )
            
            # Sort the component plan in place (Topological Dependency Sorting)
            try:
                sort_component_plan_in_place(component_plan)
            except CyclicDependencyError as e:
                self.project.mark_failed(str(e))
                return False
            
            # Save ComponentPlan (Idempotent)
            ComponentPlan.objects.update_or_create(
                project=self.project,
                defaults={'components': [c.model_dump() for c in component_plan.components]}
            )
            
            self.action_logger.log('planning', 'contract_builder', 'built_component_plan', {
                'component_count': len(component_plan.components),
                'components': [c.id for c in component_plan.components],
            })
            
            # [COMMITMENT] Register Component Plan
            manifest.register_component_plan(component_plan)

            # Step 5: Sequential Code Generation (Multi-Phase)
            self._update_status('code_generation', 'Generating Project Files (Phased)', 80)
            
            all_generated_files = {}

            # Phase 1: Backend
            phase_result = generate_backend(
                intent_spec, self.project.gemini_model,
                rag_service=rag_service, manifest=manifest,
                on_exhaustion=self._handle_exhaustion,
                action_history=self.action_logger.get_summary()
            )
            phase_files = {f.path: f.content for f in phase_result.files}
            all_generated_files.update(phase_files)
            manifest.register_generation_result(phase_result)
            
            self.action_logger.log('generation', 'backend', 'generated_files', {
                'paths': list(phase_files.keys()),
                'choices': phase_result.implementation_notes,
                'contracts': phase_result.cross_layer_contracts.model_dump() if hasattr(phase_result.cross_layer_contracts, 'model_dump') else {},
                'shapes_recorded': bool(phase_result.interface_contracts)
            })

            # Phase 2: Frontend
            phase_result = generate_frontend(
                intent_spec, self.project.gemini_model,
                rag_service=rag_service, manifest=manifest,
                on_exhaustion=self._handle_exhaustion,
                action_history=self.action_logger.get_summary()
            )
            phase_files = {f.path: f.content for f in phase_result.files}
            all_generated_files.update(phase_files)
            manifest.register_generation_result(phase_result)
            
            self.action_logger.log('generation', 'frontend', 'generated_files', {
                'paths': list(phase_files.keys()),
                'choices': phase_result.implementation_notes,
                'contracts': phase_result.cross_layer_contracts.model_dump() if hasattr(phase_result.cross_layer_contracts, 'model_dump') else {},
                'shapes_recorded': bool(phase_result.interface_contracts)
            })

            # Phase 3: Infrastructure (Derivative of Backend/Frontend choices)
            phase_result = generate_infrastructure(
                intent_spec, self.project.gemini_model,
                rag_service=rag_service, manifest=manifest,
                on_exhaustion=self._handle_exhaustion,
                action_history=self.action_logger.get_summary()
            )
            phase_files = {f.path: f.content for f in phase_result.files}
            all_generated_files.update(phase_files)
            
            self.action_logger.log('generation', 'infrastructure', 'generated_files', {
                'paths': list(phase_files.keys()),
                'choices': phase_result.implementation_notes
            })

            generated_files = all_generated_files

            self.action_logger.log('code_generation', 'generation_engine', 'generated_all_files', {
                'file_count': len(generated_files),
                'files': list(generated_files.keys())
            })

            # Stage 6: Assembling Repository
            self._update_status('assembling', 'Assembling Repository', 90)
            
            zip_path = assemble_repository(
                self.project,
                intent_spec,
                generated_files,
                manifest=manifest,
                action_history=self.action_logger.get_summary()
            )
            
            # Update project
            self.project.zip_file_path = str(zip_path)
            self.project.mark_completed()
            
            self.action_logger.log('assembling', 'builder', 'assembled_repository', {
                'zip_path': str(zip_path),
                'file_count': len(generated_files),
            })
            
            return True
            
        except Exception as e:
            error_msg = utils.format_gemini_error(e)
            logger.error(f"PIPELINE FAILURE: {error_msg}")
            
            self.project.mark_failed(error_msg)
            return False
    
    def _update_status(self, status: str, stage: str, progress: int):
        """Update project status."""
        self.project.status = status
        self.project.current_stage = stage
        self.project.progress = progress
        self.project.save()


def run_pipeline(project: Project) -> bool:
    orchestrator = PipelineOrchestrator(project)
    return orchestrator.run()
