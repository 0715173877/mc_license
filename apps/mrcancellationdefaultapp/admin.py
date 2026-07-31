from django.contrib import admin
from .models import DraftCancellationDefault, CancellationSuspensionMineralRight, CancellationDefaultDocument

@admin.register(DraftCancellationDefault)
class DraftCancellationDefaultAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(CancellationSuspensionMineralRight)
class CancellationSuspensionMineralRightAdmin(admin.ModelAdmin):
    list_display = ('legal_entity_id', 'cancellation_suspension_id', 'licence_id', 'status_id')

@admin.register(CancellationDefaultDocument)
class CancellationDefaultDocumentAdmin(admin.ModelAdmin):
    list_display = ('cancellation_default_document_id', 'cancellation_suspension', 'document_type')