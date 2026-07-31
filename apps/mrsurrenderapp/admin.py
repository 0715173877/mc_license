from django.contrib import admin
from .models import DraftSurrender, SurrenderMineralRight

@admin.register(DraftSurrender)
class DraftSurrenderAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(SurrenderMineralRight)
class SurrenderMineralRightAdmin(admin.ModelAdmin):
    list_display = ('surrender_mineral_right_id', 'licence_id', 'status_id')