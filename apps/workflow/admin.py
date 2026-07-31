from django.contrib import admin
from .models import Workflow, Stage, Action, Transition, ApplicationHistory, WorkflowModelMapping

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('workflow_id', 'workflow_name', 'abbreviation')
    search_fields = ('workflow_name', 'abbreviation')

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('stage_id', 'stage_name')

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('action_id', 'action_name')

@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    list_display = ('transition_id', 'workflow', 'current_stage', 'next_stage', 'action')
    list_filter = ('workflow',)

@admin.register(ApplicationHistory)
class ApplicationHistoryAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'stage', 'decision', 'record_created_date')
    list_filter = ('stage',)

@admin.register(WorkflowModelMapping)
class WorkflowModelMappingAdmin(admin.ModelAdmin):
    list_display = ('mapping_id', 'model_name', 'workflow')