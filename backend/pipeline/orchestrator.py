"""
Main LangGraph orchestrator for the DevScaffold pipeline.
Coordinates all agents in the correct sequence.
"""
from typing import Dict, Any
import traceback

from projects.models import Project, IntentSpec, ComponentPlan, DependencyGraph, ValidationError as ValidationErrorModel
from .agents.spec_builder import build_spec_from_prompt
from .agents.validator import validate_spec
from .agents.contract_builder import build_component_plan
from .agents.folder_contract_builder import build_folder_contracts
from .agents.dependency_graph_builder import build_dependency_graph, CyclicDependencyError
from assembly.builder import assemble_repository


class PipelineOrchestrator:
    """
    Orchestrates the entire DevScaffold pipeline.
    Each stage is executed in sequence with error handling and retry logic.
    """
    
    def __init__(self, project: Project):
        self.project = project
        self.user = project.user
        self.model_provider = project.model_provider
        
        # Check if a specific API key was selected
        if hasattr(project, '_selected_api_key') and project._selected_api_key:
            self.api_key = project._selected_api_key
        elif self.model_provider == 'gemini':
            # Fallback: Get first Gemini key from new APIKey model
            from accounts.models import APIKey
            gemini_key = APIKey.objects.filter(user=self.user, provider='gemini').first()
            self.api_key = gemini_key.get_api_key() if gemini_key else None
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
        
        if not self.api_key:
            raise ValueError(f"User does not have {self.model_provider} API key configured")
    
    def run(self, prompt: str = None) -> bool:
        """
        Run the complete pipeline.
        Returns True if successful, False otherwise.
        """
        try:
            # Use project prompt if not provided
            target_prompt = prompt or self.project.prompt
            
            # Stage 1: Build Intent Spec
            self._update_status('spec_building', 'Building Intent Spec', 10)
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
                    'constraints': intent_spec.constraints
                }
            )
            
            # Stage 2: Validate
            self._update_status('validating', 'Validating Intent Spec', 25)
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
            
            # Stage 3: Build Component Plan
            self._update_status('planning', 'Building Component Plan', 40)
            component_plan = build_component_plan(
                intent_spec,
                self.project.gemini_model,
                self.api_key
            )
            
            # Save Component Plan
            ComponentPlan.objects.create(
                project=self.project,
                components=[c.model_dump() for c in component_plan.components]
            )
            
            # Stage 4: Build Dependency Graph
            self._update_status('graph_building', 'Building Dependency Graph', 55)
            try:
                dep_graph = build_dependency_graph(component_plan)
            except CyclicDependencyError as e:
                self.project.mark_failed(str(e))
                return False
            
            # Save Dependency Graph
            DependencyGraph.objects.create(
                project=self.project,
                nodes=dep_graph.nodes,
                edges=[e.model_dump() if hasattr(e, 'model_dump') else e for e in dep_graph.edges],
                build_order=topological_sort_from_graph(dep_graph)
            )
            
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
            
            # Stage 6: Generate Code
            self._update_status('code_generation', 'Generating Code', 75)
            build_order = topological_sort_from_graph(dep_graph)
            
            from .agents.code_generator import generate_files_with_gemini
            generated_files = generate_files_with_gemini(
                intent_spec,
                component_plan,
                folder_contracts,
                build_order,
                self.project.gemini_model,
                self.api_key
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
            
            return True
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
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
