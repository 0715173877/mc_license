from django.contrib import admin
from .models import DraftRenewal, Renewal, RenewalDocument

@admin.register(DraftRenewal)
class DraftRenewalAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(Renewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ('renewal_id', 'licence_id', 'is_same_shape', 'number_of_years', 'status_id')

@admin.register(RenewalDocument)
class RenewalDocumentAdmin(admin.ModelAdmin):
    list_display = ('renewal_document_id', 'renewal', 'document_type')