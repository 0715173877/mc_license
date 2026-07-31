from django.contrib import admin
from .models import DraftQuarterlyReport, QuarterlyReport, QuarterlyReportDocument

@admin.register(DraftQuarterlyReport)
class DraftQuarterlyReportAdmin(admin.ModelAdmin):
    list_display = ('draft_id', 'user_id', 'licence_id', 'current_step', 'record_updated_date')

@admin.register(QuarterlyReport)
class QuarterlyReportAdmin(admin.ModelAdmin):
    list_display = ('quarterly_report_id', 'licence_id', 'quarter', 'year', 'status_id')

@admin.register(QuarterlyReportDocument)
class QuarterlyReportDocumentAdmin(admin.ModelAdmin):
    list_display = ('quarterly_report_document_id', 'quarterly_report', 'document_type')