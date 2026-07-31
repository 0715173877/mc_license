from django.contrib import admin
from .models import SurrenderMineralRight

@admin.register(SurrenderMineralRight)
class SurrenderMineralRightAdmin(admin.ModelAdmin):
    list_display = ('surrender_mineral_right_id', 'licence_id', 'surrender_type', 'status_id')
    list_filter = ('status_id',)