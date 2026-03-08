"""
DRF views for projects app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import FileResponse, Http404
from pathlib import Path
import threading

from .models import Project, IntentSpec
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    IntentSpecSerializer
)
from pipeline.orchestrator import run_pipeline


@api_view(['GET'])
@permission_classes([AllowAny])
def available_versions(request):
    """GET /api/projects/versions/ — Returns available framework versions for frontend dropdowns."""
    from assembly.builder import AVAILABLE_VERSIONS
    return Response(AVAILABLE_VERSIONS)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations.
    All endpoints require authentication and filter by user.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return projects owned by the authenticated user
        return Project.objects.filter(user=self.request.user).select_related(
            'intent_spec', 'component_plan'
        ).prefetch_related('validation_errors')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action == 'create':
            return ProjectCreateSerializer
        return ProjectDetailSerializer
    
    def perform_create(self, serializer):
        # Create project and automatically set user
        project = serializer.save(user=self.request.user)
        
        # Start pipeline in background thread (in production, use Celery)
        def run_pipeline_async():
            try:
                run_pipeline(project)
            except Exception as e:
                project.status = 'failed'
                project.error_message = f"Pipeline Setup Error: {str(e)}"
                project.save()
        
        thread = threading.Thread(target=run_pipeline_async)
        thread.daemon = True
        thread.start()
    
    @action(detail=True, methods=['get'])
    def intent_spec(self, request, pk=None):
        """
        GET /api/projects/{id}/intent-spec/
        Get the Intent Spec for a project.
        """
        project = self.get_object()
        
        if not hasattr(project, 'intent_spec'):
            return Response(
                {'detail': 'Intent Spec not yet generated'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = IntentSpecSerializer(project.intent_spec)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirm_spec(self, request, pk=None):
        """
        POST /api/projects/{id}/confirm-spec/
        Confirm the current Intent Spec and resume pipeline.
        """
        project = self.get_object()
        
        if project.status != 'review_required':
            return Response(
                {'detail': f'Cannot confirm specification for project in status: {project.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        project.spec_confirmed = True
        project.save()
        
        # Resume pipeline in background
        def resume_pipeline_async():
            try:
                run_pipeline(project)
            except Exception as e:
                project.status = 'failed'
                project.error_message = f"Pipeline Resume Error: {str(e)}"
                project.save()
            
        thread = threading.Thread(target=resume_pipeline_async)
        thread.daemon = True
        thread.start()
        
        return Response({'status': 'confirmed', 'message': 'Pipeline resumed'})

    @action(detail=True, methods=['put'])
    def update_intent_spec(self, request, pk=None):
        """
        PUT /api/projects/{id}/update-intent-spec/
        Update Intent Spec and trigger regeneration.
        """
        project = self.get_object()
        
        if not hasattr(project, 'intent_spec'):
            return Response(
                {'detail': 'Intent Spec not yet generated'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = IntentSpecSerializer(project.intent_spec, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Automatically confirm if updated during review
        if project.status == 'review_required':
            project.spec_confirmed = True
            project.save()
            
            # Resume pipeline in background
            def resume_pipeline_async():
                try:
                    run_pipeline(project)
                except Exception as e:
                    project.status = 'failed'
                    project.error_message = f"Pipeline Update Error: {str(e)}"
                    project.save()
                    
            thread = threading.Thread(target=resume_pipeline_async)
            thread.daemon = True
            thread.start()
            
            return Response({
                'message': 'Intent Spec updated and confirmed. Pipeline resumed.',
                'intent_spec': serializer.data
            })
        
        return Response({
            'message': 'Intent Spec updated.',
            'intent_spec': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        GET /api/projects/{id}/status/
        Get current pipeline status for polling.
        """
        project = self.get_object()
        
        return Response({
            'status': project.status,
            'current_stage': project.current_stage,
            'progress': project.progress,
            'error_message': project.error_message
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        POST /api/projects/{id}/cancel/
        Cancel a running pipeline.
        """
        project = self.get_object()
        if project.status in ['completed', 'failed']:
            return Response(
                {'detail': f'Cannot cancel project in status: {project.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project.mark_failed("Cancelled by user")
        return Response({'status': 'cancelled'})
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        GET /api/projects/{id}/download/
        Download the generated ZIP file.
        """
        project = self.get_object()
        
        if not project.zip_file_path:
            return Response(
                {'detail': 'Project not yet completed or ZIP file not available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        zip_path = Path(project.zip_file_path)
        
        if not zip_path.exists():
            return Response(
                {'detail': 'ZIP file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return file response
        response = FileResponse(
            open(zip_path, 'rb'),
            as_attachment=True,
            filename=f"{project.name or f'project_{project.id}'}.zip"
        )
        return response

    @action(detail=True, methods=['get'])
    def browse_files(self, request, pk=None):
        """
        GET /api/projects/{id}/browse-files/
        List all files in the generated repository.
        """
        project = self.get_object()
        
        if not project.repo_directory:
            return Response(
                {'detail': 'Project repository not yet created'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        from django.core.files.storage import default_storage
        
        def get_file_tree(prefix, root_prefix):
            items = []
            try:
                dirs, files = default_storage.listdir(prefix)
                
                # Handle files
                for f in sorted(files):
                    if f in ('.git', '__pycache__', 'manifest.json'):
                        continue
                    full_p = f"{prefix}/{f}".replace('//', '/')
                    rel_p = full_p.replace(root_prefix, '').lstrip('/')
                    items.append({
                        'name': f,
                        'path': rel_p,
                        'is_dir': False
                    })
                
                # Handle directories
                for d in sorted(dirs):
                    if d in ('.git', '__pycache__'):
                        continue
                    full_p = f"{prefix}/{d}".replace('//', '/')
                    rel_p = full_p.replace(root_prefix, '').lstrip('/')
                    items.append({
                        'name': d,
                        'path': rel_p,
                        'is_dir': True,
                        'children': get_file_tree(full_p, root_prefix)
                    })
            except Exception as e:
                logger.error(f"Error listing storage {prefix}: {e}")
                
            return items
            
        tree = get_file_tree(project.repo_directory, project.repo_directory)
        return Response(tree)

    @action(detail=True, methods=['get'])
    def read_file(self, request, pk=None):
        """
        GET /api/projects/{id}/read-file/?path=filename
        Read content of a specific file.
        """
        project = self.get_object()
        file_path_rel = request.query_params.get('path')
        
        if not file_path_rel:
            return Response(
                {'detail': 'File path is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not project.repo_directory:
            return Response(
                {'detail': 'Project repository not yet created'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        from django.core.files.storage import default_storage
        storage_path = f"{project.repo_directory}/{file_path_rel}".replace('//', '/')
        
        if not default_storage.exists(storage_path):
            return Response(
                {'detail': 'File not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        try:
            with default_storage.open(storage_path, 'r') as f:
                content = f.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
            
            # Determine language for Monaco
            ext = Path(file_path_rel).suffix.lower()
            language = 'plaintext'
            if ext in ['.js', '.jsx']: language = 'javascript'
            elif ext in ['.ts', '.tsx']: language = 'typescript'
            elif ext == '.py': language = 'python'
            elif ext == '.html': language = 'html'
            elif ext == '.css': language = 'css'
            elif ext == '.json': language = 'json'
            elif ext == '.md': language = 'markdown'
            elif ext == '.yml' or ext == '.yaml': language = 'yaml'
            
            return Response({
                'content': content,
                'language': language,
                'path': file_path_rel
            })
        except Exception as e:
            return Response(
                {'detail': f'Error reading file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
