from django.contrib import admin
from .models import DraftExtension, ExtensionToCommenceMining

@admin.register(DraftExtension)
class DraftExtensionAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(ExtensionToCommenceMining)
class ExtensionToCommenceMiningAdmin(admin.ModelAdmin):
    list_display = ('extension_to_commence_mining_id', 'licence_id', 'status_id')