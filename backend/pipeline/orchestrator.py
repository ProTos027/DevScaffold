"""
Main LangGraph orchestrator for the DevScaffold pipeline.
Coordinates all agents in the correct sequence.
"""
from typing import Any
import traceback

from projects.models import Project, IntentSpec, ComponentPlan, DependencyGraph, ValidationError as ValidationErrorModel
from .agents.spec_builder import build_spec_from_prompt
from .agents.validator import validate_spec
from .agents.contract_builder import build_component_plan
from .agents.folder_contract_builder import build_folder_contracts
from .agents.dependency_graph_builder import build_dependency_graph, CyclicDependencyError
from assembly.builder import assemble_repository
from .action_logger import ActionLogger
from .rag_service import RAGService


class PipelineOrchestrator:
    """
    Orchestrates the entire DevScaffold pipeline.
    Each stage is executed in sequence with error handling and retry logic.
    """
    
    def __init__(self, project: Project):
        self.project = project
        self.user = project.user
        self.model_provider = project.model_provider
        self.api_key = None
        self.action_logger = ActionLogger(project)
        
        # Priority 1: Persistent API key linked to the project
        if hasattr(project, 'gemini_api_key') and project.gemini_api_key:
            self.api_key = project.gemini_api_key.get_api_key()
            
        # Priority 2: In-memory transient key (for immediate creation flows)
        if not self.api_key and hasattr(project, '_selected_api_key') and project._selected_api_key:
            self.api_key = project._selected_api_key
            
        # Priority 3: Fallback to first available valid Gemini key
        if not self.api_key and self.model_provider == 'gemini':
            from accounts.models import APIKey
            # Filter for keys that actually have an encrypted value
            gemini_keys = APIKey.objects.filter(
                user=self.user, 
                provider='gemini'
            ).exclude(api_key_encrypted='')
            
            gemini_key = gemini_keys.first()
            if gemini_key:
                self.api_key = gemini_key.get_api_key()
        
        if not self.api_key:
            # Check if they have ANY keys at all (even empty ones) for better error messaging
            from accounts.models import APIKey
            total_keys = APIKey.objects.filter(user=self.user, provider=self.model_provider).count()
            if total_keys > 0:
                raise ValueError(f"Found {total_keys} keys, but none contain a valid value. Please re-register your API key in the Secret Vault.")
            else:
                raise ValueError(f"No {self.model_provider} API key found. Please add one in the Secret Vault.")
    
    def run(self, prompt: str = None) -> bool:
        """
        Run the complete pipeline.
        Returns True if successful, False otherwise.
        """
        try:
            # Use project prompt if not provided
            target_prompt = prompt or self.project.prompt
            
            # Clear previous action logs for rerun consistency
            self.action_logger.clear()
            
            # Stage 1: Build or Load Intent Spec
            if hasattr(self.project, 'intent_spec') and (self.project.spec_confirmed or self.project.status == 'review_required'):
                self._update_status('spec_loading', 'Loading Intent Spec', 10)
                spec_model = self.project.intent_spec
                from .schemas import IntentSpecSchema, DataEntity
                intent_spec = IntentSpecSchema(
                    project_type=spec_model.project_type,
                    complexity=spec_model.complexity,
                    stack=spec_model.stack,
                    features=spec_model.features,
                    architecture=spec_model.architecture,
                    data_entities=[DataEntity(**e) for e in spec_model.data_entities],
                    constraints=spec_model.constraints,
                    vague_intent=spec_model.vague_intent,
                    explanation=spec_model.explanation
                )
            else:
                self._update_status('spec_building', 'Building Intent Spec', 15)
                intent_spec = build_spec_from_prompt(
                    target_prompt,
                    self.project.gemini_model,
                    self.api_key
                )
            
            # Save Intent Spec (Essential: Save BEFORE validation so user sees what was parsed)
            spec_obj, created = IntentSpec.objects.update_or_create(
                project=self.project,
                defaults={
                    'project_type': intent_spec.project_type,
                    'complexity': intent_spec.complexity,
                    'stack': intent_spec.stack,
                    'features': intent_spec.features,
                    'architecture': intent_spec.architecture,
                    'data_entities': [e.model_dump() for e in intent_spec.data_entities],
                    'constraints': intent_spec.constraints,
                    'vague_intent': intent_spec.vague_intent,
                    'explanation': intent_spec.explanation
                }
            )
            
            # Log spec building action
            self.action_logger.log('spec_building', 'spec_builder', 'built_intent_spec', {
                'project_type': intent_spec.project_type,
                'backend': intent_spec.stack.get('backend'),
                'backend_version': intent_spec.stack.get('backend_version'),
                'frontend': intent_spec.stack.get('frontend'),
                'frontend_version': intent_spec.stack.get('frontend_version'),
                'database': intent_spec.stack.get('database'),
                'complexity': intent_spec.complexity,
                'features': intent_spec.features,
            })
            
            # Always pause if not confirmed
            if not self.project.spec_confirmed:
                self._update_status('review_required', 'Review Specification Required', 30)
                return True # Stop but not failed
            validation_result = validate_spec(intent_spec)
            
            if not validation_result.is_valid:
                # Clear old validation errors
                ValidationErrorModel.objects.filter(project=self.project).delete()
                
                # Save new validation errors
                for error in validation_result.errors:
                    ValidationErrorModel.objects.create(
                        project=self.project,
                        rule_name=error.split(':')[0],
                        error_message=error,
                        severity='error'
                    )
                self.project.mark_failed(f"Validation failed: {'; '.join(validation_result.errors)}")
                return False
            
            # Clear any previous validation errors if now valid
            ValidationErrorModel.objects.filter(project=self.project).delete()
            
            self.action_logger.log('validating', 'validator', 'validation_passed', {
                'rules_checked': len(validation_result.errors) if hasattr(validation_result, 'errors') else 0
            })
            
            # Stage 3: Build Component Plan
            self._update_status('planning', 'Building Component Plan', 40)
            component_plan = build_component_plan(
                intent_spec,
                self.project.gemini_model,
                self.api_key
            )
            
            # Save ComponentPlan (Idempotent)
            ComponentPlan.objects.update_or_create(
                project=self.project,
                defaults={'components': [c.model_dump() for c in component_plan.components]}
            )
            
            self.action_logger.log('planning', 'contract_builder', 'built_component_plan', {
                'component_count': len(component_plan.components),
                'components': [c.id for c in component_plan.components],
            })
            
            # Stage 4: Build Dependency Graph
            self._update_status('graph_building', 'Building Dependency Graph', 55)
            try:
                dep_graph = build_dependency_graph(component_plan)
            except CyclicDependencyError as e:
                self.project.mark_failed(str(e))
                return False
            
            # Save Dependency Graph (Idempotent)
            DependencyGraph.objects.update_or_create(
                project=self.project,
                defaults={
                    'nodes': dep_graph.nodes,
                    'edges': [e.model_dump() if hasattr(e, 'model_dump') else e for e in dep_graph.edges],
                    'build_order': topological_sort_from_graph(dep_graph)
                }
            )
            
            self.action_logger.log('graph_building', 'dependency_graph_builder', 'built_dependency_graph', {
                'node_count': len(dep_graph.nodes),
                'edge_count': len(dep_graph.edges),
                'build_order': topological_sort_from_graph(dep_graph),
            })
            
            # Stage 5: Build Folder Contracts
            self._update_status('folder_contracts', 'Building Folder Contracts', 60)
            folder_contracts = build_folder_contracts(
                intent_spec,
                component_plan,
                self.project.gemini_model,
                self.api_key
            )
            
            # Save Folder Contracts
            from projects.models import FolderContract
            FolderContract.objects.filter(project=self.project).delete() # Clear old ones
            for contract in folder_contracts.contracts:
                FolderContract.objects.create(
                    project=self.project,
                    component_id=contract.component_id,
                    folder_path=contract.folder,
                    files=contract.files,
                    responsibilities=contract.responsibilities,
                    dependencies=contract.dependencies,
                    interfaces=contract.interfaces,
                    models_used=contract.models_used
                )
            
            self.action_logger.log('folder_contracts', 'folder_contract_builder', 'built_folder_contracts', {
                'contract_count': len(folder_contracts.contracts),
                'contracts': [c.component_id for c in folder_contracts.contracts],
            })
            
            # Stage 6: Generate Code
            self._update_status('code_generation', 'Generating Code', 75)
            build_order = topological_sort_from_graph(dep_graph)
            
            # Initialize RAG knowledge base for framework-specific context
            rag_service = None
            try:
                frameworks = []
                if intent_spec.stack.get('backend'):
                    frameworks.append(intent_spec.stack['backend'])
                if intent_spec.stack.get('frontend'):
                    frameworks.append(intent_spec.stack['frontend'])
                rag_service = RAGService(api_key=self.api_key)
                rag_service.load(frameworks=frameworks)
            except Exception as e:
                print(f"⚠️ RAG service failed to load (non-fatal): {e}")
                rag_service = None
            
            from .agents.code_generator import generate_files_with_gemini
            generated_files = generate_files_with_gemini(
                intent_spec,
                component_plan,
                folder_contracts,
                build_order,
                self.project.gemini_model,
                self.api_key,
                action_logger=self.action_logger,
                rag_service=rag_service
            )
            
            # Stage 7: Assemble Repository
            self._update_status('assembling', 'Assembling Repository', 90)
            zip_path = assemble_repository(
                self.project,
                intent_spec,
                generated_files
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
            from .utils import format_gemini_error
            clean_msg = format_gemini_error(e)
            
            # Additional context mapping (optional, clean_msg might already handle 503/429)
            error_str = str(e).lower()
            if "status: completed" in error_str: # Special case for already finished projects
                error_msg = clean_msg
            elif "429" in error_str or "quota" in error_str:
                error_msg = f"API Quota Exhausted: {clean_msg}"
            elif "503" in error_str:
                error_msg = f"Gemini Overloaded: {clean_msg}"
            else:
                error_msg = clean_msg
            
            print(f"❌ PIPELINE FAILURE: {error_msg}")
            # Log the full traceback for debugging but don't show to user in mark_failed
            import logging
            logging.error(f"Pipeline error: {traceback.format_exc()}")
            
            self.project.mark_failed(error_msg)
            return False
    
    def _update_status(self, status: str, stage: str, progress: int):
        """Update project status."""
        self.project.status = status
        self.project.current_stage = stage
        self.project.progress = progress
        self.project.save()


def topological_sort_from_graph(dep_graph) -> list:
    """Extract build order from dependency graph."""
    from .agents.dependency_graph_builder import topological_sort, DependencyEdge
    
    # Edges might already be DependencyEdge objects or dicts
    edges = []
    for e in dep_graph.edges:
        if isinstance(e, DependencyEdge):
            edges.append(e)
        elif isinstance(e, dict):
            edges.append(DependencyEdge(**e))
        else:
            # If it's already a Pydantic model, convert to dict first
            edges.append(DependencyEdge(**e.model_dump()))
    
    return topological_sort(dep_graph.nodes, edges)


def run_pipeline(project: Project) -> bool:
    """
    Convenience function to run the pipeline for a project.
    
    Args:
        project: Project instance
    
    Returns:
        True if successful, False otherwise
    """
    orchestrator = PipelineOrchestrator(project)
    return orchestrator.run()
