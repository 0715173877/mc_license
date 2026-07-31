from rest_framework import serializers
from .models import DraftQuarterlyReport, QuarterlyReport, QuarterlyReportDocument

class DraftQuarterlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DraftQuarterlyReport
        fields = '__all__'
        read_only_fields = ['draft_id', 'record_created_date', 'record_updated_date']

class QuarterlyReportDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuarterlyReportDocument
        fields = '__all__'
        read_only_fields = ['quarterly_report_document_id', 'record_created_date']

class QuarterlyReportSerializer(serializers.ModelSerializer):
    documents = QuarterlyReportDocumentSerializer(source='quarterlyreportdocument_set', many=True, read_only=True)

    class Meta:
        model = QuarterlyReport
        fields = '__all__'
        read_only_fields = [
            'quarterly_report_id', 'record_created_date', 'record_updated_date'
        ]

class QuarterlyReportCreateSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = QuarterlyReport
        fields = [
            'licence_id', 'quarter', 'year', 'status_id',
            'record_created_by', 'guid', 'documents'
        ]
        extra_kwargs = {
            'status_id': {'default': 1},
        }

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        report = QuarterlyReport.objects.create(**validated_data)
        for doc_data in documents_data:
            QuarterlyReportDocument.objects.create(
                quarterly_report=report,
                document_type=doc_data.get('document_type', 'Report'),
                document_url=doc_data.get('document_url'),
                file_name=doc_data.get('file_name', ''),
                record_created_by=validated_data.get('record_created_by')
            )
        return report