from django.contrib import admin
from .models import DraftEnlargement, EnlargeMineralRight

@admin.register(DraftEnlargement)
class DraftEnlargementAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(EnlargeMineralRight)
class EnlargeMineralRightAdmin(admin.ModelAdmin):
    list_display = ('enlarge_mineral_right_id', 'licence_id', 'status_id')