from django.contrib import admin
from .models import EnlargeMineralRight

@admin.register(EnlargeMineralRight)
class EnlargeMineralRightAdmin(admin.ModelAdmin):
    list_display = ('enlarge_mineral_right_id', 'licence_id', 'status_id', 'application_date')
    list_filter = ('status_id',)