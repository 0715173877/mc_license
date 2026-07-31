from django.contrib import admin
from .models import DraftSuspension, SuspendMineralRight, SuspensionDocument

@admin.register(DraftSuspension)
class DraftSuspensionAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(SuspendMineralRight)
class SuspendMineralRightAdmin(admin.ModelAdmin):
    list_display = ('suspend_mineral_right_id', 'licence_id', 'suspension_reason', 'status_id')

@admin.register(SuspensionDocument)
class SuspensionDocumentAdmin(admin.ModelAdmin):
    list_display = ('suspension_document_id', 'suspend_mineral_right', 'document_type')