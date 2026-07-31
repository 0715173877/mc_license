from django.contrib import admin
from .models import DraftPmlTechSupport, PmlTechnicalSupport, PmlTechSupportDocument

@admin.register(DraftPmlTechSupport)
class DraftPmlTechSupportAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(PmlTechnicalSupport)
class PmlTechnicalSupportAdmin(admin.ModelAdmin):
    list_display = ('pml_technical_support_id', 'licence_id', 'status_id')

@admin.register(PmlTechSupportDocument)
class PmlTechSupportDocumentAdmin(admin.ModelAdmin):
    list_display = ('pml_tech_support_document_id', 'pml_technical_support', 'document_type')