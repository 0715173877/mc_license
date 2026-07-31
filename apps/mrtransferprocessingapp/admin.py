from django.contrib import admin
from .models import TransferMineralRight

@admin.register(TransferMineralRight)
class TransferMineralRightAdmin(admin.ModelAdmin):
    list_display = ('transfer_mineral_right_id', 'licence_id', 'status_id')
    list_filter = ('status_id',)