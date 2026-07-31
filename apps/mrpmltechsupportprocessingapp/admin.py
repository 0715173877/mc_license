from django.contrib import admin
from .models import PmlTechnicalSupport

@admin.register(PmlTechnicalSupport)
class PmlTechnicalSupportAdmin(admin.ModelAdmin):
    list_display = ('pml_technical_support_id', 'licence_id', 'is_fresh_application', 'status_id')
    list_filter = ('status_id', 'is_fresh_application')