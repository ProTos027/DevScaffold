"""
DRF views for projects app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations.
    All endpoints require authentication and filter by user.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return projects owned by the authenticated user
        return Project.objects.filter(user=self.request.user).select_related(
            'intent_spec', 'component_plan', 'dependency_graph'
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
            run_pipeline(project)
        
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
        
        # TODO: Trigger regeneration from validation stage
        
        return Response({
            'message': 'Intent Spec updated. Regeneration not yet implemented.',
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
