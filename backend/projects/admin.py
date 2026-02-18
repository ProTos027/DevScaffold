from django.contrib import admin
from .models import (
    Project, IntentSpec, ComponentPlan, 
    DependencyGraph, FolderContract, ValidationError
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'status', 'progress', 'created_at')
    list_filter = ('status', 'model_provider', 'gemini_model')
    search_fields = ('name', 'prompt', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'deletion_scheduled_at')


@admin.register(IntentSpec)
class IntentSpecAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'project_type', 'complexity', 'version', 'created_at')
    list_filter = ('project_type', 'complexity')


@admin.register(ComponentPlan)
class ComponentPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'generated_at')


@admin.register(DependencyGraph)
class DependencyGraphAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'generated_at')


@admin.register(FolderContract)
class FolderContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'component_id', 'folder_path', 'generated_at')
    list_filter = ('component_id',)


@admin.register(ValidationError)
class ValidationErrorAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'rule_name', 'severity', 'created_at')
    list_filter = ('severity', 'rule_name')

