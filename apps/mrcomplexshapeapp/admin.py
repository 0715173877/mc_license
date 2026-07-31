from django.contrib import admin
from .models import DraftComplexShape, ComplexShapeDocument

@admin.register(DraftComplexShape)
class DraftComplexShapeAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(ComplexShapeDocument)
class ComplexShapeDocumentAdmin(admin.ModelAdmin):
    list_display = ('complex_shape_document_id', 'licence_id', 'document_type', 'status_id')